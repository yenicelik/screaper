use std::{sync::Arc, thread, time::Duration, time::Instant, collections::HashSet};

use std::sync::atomic::{AtomicUsize, Ordering};
use clap::{App, Arg, ArgMatches, SubCommand};
use deadpool::{
    managed::{Pool as ManagedPool, RecycleResult},
    unmanaged::Pool as UnmanagedPool,
};
use futures::future::{FutureExt, TryFutureExt};
use futures::stream::{iter, repeat_with, unfold, StreamExt};
use rand::thread_rng;
use rand::seq::SliceRandom;
use regex::Regex;
use reqwest::{Client, Error as ReqwestError};
use select::document::Document;
use select::predicate::Name;
use serde::Deserialize;
use url::{Url, ParseError};
use url_normalizer::normalize;

use screaper_data::{Connection, ConnectionError, UrlRecord, MarkupRecord, UrlRecordStatus, UrlReferralRecord};

fn is_number(string: String) -> Result<(), String> {
    let regex = Regex::new(r"^[0-9]+$").unwrap();

    if regex.is_match(&string) {
        Ok(())
    } else {
        Err("the provided value must be a valid number".to_string())
    }
}

pub fn app() -> App<'static, 'static> {
    SubCommand::with_name("run")
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct Proxy {
    ip: String,
    port: String,
    // ping: usize,
    google_error: String,
    // google_status: usize,
    // google_total_time: usize,
    // anonymity: String,
    // working_count: usize,
    // uptime: f32,
    // recheck_count: usize,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct ProxyResponse {
    date: String,
    proxies: Vec<Proxy>
}

struct DatabaseManager {
    url: String,
}

#[async_trait::async_trait]
impl deadpool::managed::Manager<Connection, ConnectionError> for DatabaseManager {
    async fn create(&self) -> Result<Connection, ConnectionError> {
        screaper_data::connection(&self.url)
    }

    async fn recycle(&self, obj: &mut Connection) -> RecycleResult<ConnectionError> {
        Ok(())
    }
}

pub async fn main<'a>(globals: &ArgMatches<'a>, args: &ArgMatches<'a>) {
    let connections = ManagedPool::new(
        DatabaseManager {
            url: globals.value_of("database_url").unwrap().to_owned(),
        },
        10,
    );

    // Read file that reads all blacklisted URLs
    let blacklist_urls_file = std::fs::File::open("notebooks/notebooks_20201223_popular_websites/popular_websites.yaml").unwrap();
    let blacklist_urls_readfile: serde_yaml::Value  = serde_yaml::from_reader(blacklist_urls_file).unwrap();
    // let blacklist_urls: HashSet<String> = blacklist_urls_readfile["websites"].as_sequence().unwrap().to_owned()
    //    .iter().map(|x| x.as_str().unwrap().to_owned()).collect();
    let blacklist_urls: HashSet<String> = blacklist_urls_readfile["websites"].as_sequence().unwrap().into_iter().map(|x| x.as_str().unwrap().to_owned()).collect::<HashSet<_>>();
    let blacklist_url_atomic_reference = std::sync::Arc::new(blacklist_urls);

    let mut rng = thread_rng();
    // "(?i)\b((?:(https|https)?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    let re = Regex::new(
        &regex::escape(r"(?i)\b((?:(https|https)?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'.,<>?«»“”‘’]))")
    ).unwrap();

    // `socks4` protocol currently unsupported by reqwest
    let proxyResponse: ProxyResponse = reqwest::get("https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json").await.unwrap().json::<ProxyResponse>().await.unwrap();
    /*let clients = proxyResponse.proxies.into_iter().filter(|proxy| proxy.google_error == "no").map(|proxy| Arc::new(
        Client::builder().timeout(Duration::from_secs(20))
        .user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
        .build().unwrap()
    )).collect::<Vec<_>>();*/
    let clients = proxyResponse.proxies.into_iter().filter(|proxy| proxy.google_error == "no").map(|proxy| Arc::new(
        Client::builder().timeout(Duration::from_secs(20))
        .proxy(reqwest::Proxy::all(&format!("socks5://{}:{}", proxy.ip, proxy.port)).unwrap())
        .user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
        .build().unwrap()
    )).collect::<Vec<_>>();

    // No proxy
    // Number of spiders 1 = 0.15 requests / second
    // Number of spiders 5 = 0.37 requests / second // 0.2 requests / second
    // Number of spiders 10 = 0.55 requests / second // 0.52 requests / second // 0.42 requests / second 
    // Number of spiders 20 = 0.833 requests / second // 0.4 requests / second 

    // Proxy
    // Number of spiders 1000 = 1.87 requests / second
    let number_of_spiders = 500;

    let now = Instant::now();
    let counter = Arc::new(AtomicUsize::new(1));

    println!("Connecting to database...");
    unfold(connections.clone(), |pool| async {
        let records = {
            let connection = pool.get().await.unwrap();
            UrlRecord::ready(&connection, 4000).unwrap()
        };
        Some((iter(records), pool))
    })
    .flatten()
    .for_each_concurrent(number_of_spiders, |mut record| {

        // TODO: Remove this proxy if there are too many failed retries
        let client = clients.choose(&mut rng).unwrap().clone();

        let connections = connections.clone();
        let blacklist_reference_copy = blacklist_url_atomic_reference.clone();
        let counter_copy = counter.clone();

        if (counter_copy.load(Ordering::Relaxed) as usize % 10) == 0 {
            let req_per_sec = (counter_copy.load(Ordering::Relaxed) as f32) / (now.elapsed().as_secs() + 1) as f32;
            println!("Seconds {} -- Items {} -- {} requests/s -- {} requests/min -- {} requests/h -- {} requests/day", 
                counter_copy.load(Ordering::Relaxed), now.elapsed().as_secs(), 
                req_per_sec, 
                (req_per_sec * 60.0) as i16, 
                (req_per_sec * 60.0 * 60.0) as i16, 
                (req_per_sec * 60.0 * 60.0 * 24.0) as i16
            );
        }


        async move {
            tokio::spawn(async move {

                let connection = connections.get().await.unwrap();

                let mut failed = false;

                record.set_status(UrlRecordStatus::Processing);
                let insert_result = record.save(&connection);
                match insert_result {
                    Ok(()) => (),
                    Err(e) => {
                        println!("{}", e);
                        failed = true;
                        panic!();
                    }
                }


                // If panic happens here, increase retry amount by one
                let response_result = client.get(record.data()).send().await;
                counter_copy.fetch_add(1 as usize, Ordering::Relaxed);

                match response_result {
                    Ok(response) => {

                        // If response code is not "OK", then set retries and continue
                        if (!response.status().is_success()) {
                            failed = true;
                        }

                        // Continue to next url if failed somehow
                        if (failed) {
                            println!("failed {:?}", record.data());
                            // println!("{:?}", response.text().await.unwrap());
                            record.set_status(UrlRecordStatus::Ready);
                            let insert_result = record.save(&connection);
                            match insert_result {
                                Ok(()) => (),
                                Err(e) => {
                                    println!("{}", e);
                                    record.set_status(UrlRecordStatus::Failed);
                                    let insert_result = record.save(&connection);
                                    match insert_result {
                                        Ok(()) => (),
                                        Err(e) => {
                                            println!("{}", e);
                                        }
                                    }
                                }
                            }
                            return;
                        }

                        let document = response.text().await.unwrap();

                        let mut collected_urls: HashSet<Url> = HashSet::new();
        
                        let base_url: String = record.data().to_string();
                        let parsed_base_url: Url = Url::parse(&base_url).unwrap();
                        let parsed_domain = parsed_base_url.host_str().unwrap();
        
                        // Parse all href links from the response 
                        Document::from(document.as_str())
                        .find(Name("a"))
                        .filter_map(|n| n.attr("href"))
                        .for_each(|x| {
        
                            let mut current_url: String = x.to_string();
        
                            let first_character = current_url.chars().next();


                            match first_character {
                                Some(v) => {
        
                                    // If the first element of the URL is a "/", then prepend the host
                                    if v == '/' {
                                        if base_url.chars().last().unwrap() == '/' {
                                            current_url = base_url.clone() + &current_url;
                                        } else {
                                            current_url = base_url.clone() + &current_url[1..];
                                        }
                                    } 
                                    if v != '#' && base_url != "javascript:void(0)"{
        
                                        // Turn x into a URL object
                                        let parsed_url = Url::parse(&current_url);
        
                                        // TODO take out all utm parameters (see python code) 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'
        
                                        // Normalize all links => there is this rust package that does ISO normalization
                                        match parsed_url {
                                            Ok(v) => {
                                                let url: Result<Url, _> = normalize(v);
                                                match url {
                                                    Ok(v) => {
                                                        collected_urls.insert(v);
                                                    },
                                                    Err(e) => {
                                                        println!("URL not parsed");
                                                        // println!("{:?}", e);
                                                        println!("{:?}", x);
                                                    }
                                                }
                                            }, 
                                            Err(e) => {
                                                println!("URL not normalized");
                                                // println!("{:?}", e);
                                                println!("{:?}", x);
                                            }
                                        }
                                    }
        
                                },
                                None => {}
                            }
        
                        });
        
                        // Also parse the rawtext for any strings that match the URL regex scheme
                        // Parse all links extracted as regex from the response
                        // We can leave this for now, let's see how much performance this eats up
                        /*
                        for cap in re.captures_iter(document) {
                            
                            let url = URL.parse(cap);
                            // Normalize all links => there is this rust package that does ISO normalization
                            // TODO take out all utm parameters (see python code) 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'
                            url = url_normalize(url);
                            collected_urls.insert_into(url);
        
                            println!("URL in plaintext found: {}", &cap[0]);
                        }
                        */
        
                        // For all collected urls, insert them into the database
                        for url in &collected_urls {
        
                            // Mark them as skipped if they are contained in this list
                            // mark the item if it is in this list as skipped https://github.com/yenicelik/screaper/blob/rust/notebooks/notebooks_20201223_popular_websites/popular_websites.yaml
        
                            let status: UrlRecordStatus;
        
                            // Skip certain URLs 
                            // These unwrap should work because we have prepended host urls before
                            let parsed_domain_result = url.host_str();

                            match parsed_domain_result {

                                Some(parsed_domain) => {

                                    // Maybe apply faster logic somehow
                                    if (blacklist_reference_copy.contains(&parsed_domain.to_owned()) || &parsed_domain[..4] == "tel:" || &parsed_domain[..7] == "mailto:") {
                                        // println!("Ignore");
                                        // println!("{:?}", parsed_domain);
                                        status = UrlRecordStatus::Ignored;
                                    } else {
                                        status = UrlRecordStatus::Ready;
                                    }
                                    let depth = record.depth() + 1;
                
                                    // Save all newly found URLs into the database
                                    let url_record_response = UrlRecord::get_or_insert(&connection, url.as_str(), status, depth as i32);
                                    match url_record_response {
                                        Ok(url_record) => {
                                            // Save all newly found URLs into the database queue
                                            // Increase count if record already exists
                                            let insert_result = UrlReferralRecord::get_or_insert(&connection, record.id(), url_record.id(), 1);
                                            match insert_result {
                                                Ok(_) => (),
                                                Err(e) => {
                                                    println!("Insert URL Referral Record");
                                                    println!("{}", e);
                                                    record.set_status(UrlRecordStatus::Failed);
                                                    let insert_result = record.save(&connection);
                                                    match insert_result {
                                                        Ok(()) => (),
                                                        Err(e) => {
                                                            println!("{}", e);
                                                        }
                                                    }
                                                }
                                            }
                
                                        },
                                        Err(e) => {
                                            println!("Get or Insert URL Record");
                                            println!("{}", e);
                                            record.set_status(UrlRecordStatus::Failed);
                                            let insert_result = record.save(&connection);
                                            match insert_result {
                                                Ok(()) => (),
                                                Err(e) => {
                                                    println!("{}", e);
                                                }
                                            }                        
                                        }
                                    }
                
                                    // Save markdown to database // Insert should always call the "0" status (a python script later will modify this)
                                    let insert_result = MarkupRecord::get_or_insert(&connection, record.id(), &document.to_string(), 0 as i16);
                                    match insert_result {
                                        Ok(_) => {
                                            record.set_status(UrlRecordStatus::Processed);
                                            let insert_result = record.save(&connection);
                                            match insert_result {
                                                Ok(()) => (),
                                                Err(e) => {
                                                    println!("{}", e);
                                                }
                                            }
                                        },
                                        Err(e) => {
                                            println!("Insert Markup Record");
                                            println!("{}", e);
                                            record.set_status(UrlRecordStatus::Failed);
                                            let insert_result = record.save(&connection);
                                            match insert_result {
                                                Ok(()) => (),
                                                Err(e) => {
                                                    println!("{}", e);
                                                }
                                            }
                                        }
                                    }

                                },
                                None => {
                                    // println!("No host: {:?}", url.as_str());
                                }
                            }
                        }


                        


                    },
                    Err(e) => {
                        record.set_retries(record.retries() + 1);
                        let insert_result = record.save(&connection);
                            match insert_result {
                                Ok(()) => (),
                                Err(e) => {
                                    println!("{}", e);
                                }
                            }
                    }
                }

                // This easily makes VSCode crash, perhaps do this later
                // println!("{:?}", response.text().await.unwrap());
                // panic!();

            })
            .await
            .ok();
        }
    })
    .await;
}
