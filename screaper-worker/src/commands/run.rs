/**
 * No proxy
 * Number of spiders 1 = 0.15 requests / second
 * Number of spiders 5 = 0.37 requests / second // 0.2 requests / second
 * Number of spiders 10 = 0.55 requests / second // 0.52 requests / second // 0.42 requests / second 
 * Number of spiders 20 = 0.833 requests / second // 0.4 requests / second 
 * Proxy
 * Number of spiders 1000 = 1.87 requests / second
 * 500 spiders leads to ca 60k requests / day
 * 1000 spiders leads to ca 60k requests / day
 * All inserts commented out: Seconds 680 -- Items 20 -- 32.38095 requests/s -- 1942 requests/min -- 116571 requests/h -- 2797714 requests/day
*/
use std::{sync::Arc, time::Duration, time::Instant, collections::HashSet};

use std::sync::atomic::{AtomicUsize, Ordering};
use clap::{App, ArgMatches, SubCommand};
use deadpool::{
    managed::{Pool as ManagedPool, RecycleResult}
};
use futures::stream::{iter, unfold, StreamExt};
use rand::thread_rng;
use rand::seq::SliceRandom;
use reqwest::{Client};
use select::document::Document;
use select::predicate::Name;
use serde::Deserialize;
use url::{Url};
use url_normalizer::normalize;

use screaper_data::{Connection, ConnectionError, UrlRecord, MarkupRecord, UrlRecordStatus, UrlReferralRecord};

pub fn app() -> App<'static, 'static> {
    SubCommand::with_name("run")
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct Proxy {
    ip: String,
    port: String,
    google_error: String,
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

pub async fn run<'a>(globals: &ArgMatches<'a>, _args: &ArgMatches<'a>) {

    println!("Running...");

    let connections = ManagedPool::new(
        DatabaseManager {
            url: globals.value_of("database_url").unwrap().to_owned(),
        },
        10,
    );

    // Read file that reads all blacklisted URLs
    let blacklist_urls_file = std::fs::File::open("notebooks/notebooks_20201223_popular_websites/popular_websites.yaml").unwrap();
    let blacklist_urls_readfile: serde_yaml::Value  = serde_yaml::from_reader(blacklist_urls_file).unwrap();
    let original_blacklist_urls: HashSet<String> = blacklist_urls_readfile["websites"].as_sequence().unwrap().into_iter().map(|x| x.as_str().unwrap().to_owned()).collect::<HashSet<_>>();
    let www_extended_blacklist_urls: HashSet<String> = original_blacklist_urls.iter().map(|x| "www.".to_string() + &x).collect::<HashSet<String>>();
    let blacklist_urls: HashSet<String> = original_blacklist_urls.union(&www_extended_blacklist_urls).into_iter().map(|x| x.to_owned()).collect::<HashSet<_>>();

    let blacklist_url_atomic_reference = std::sync::Arc::new(blacklist_urls);
    let mut rng = thread_rng();
    
    println!("Collecting proxies...");
    let proxy_response: ProxyResponse = reqwest::get("https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json").await.unwrap().json::<ProxyResponse>().await.unwrap();
    println!("Number of clients {:?}", &proxy_response.proxies.len());
    let clients = proxy_response.proxies.into_iter().filter(|proxy| proxy.google_error == "no").map(|_proxy| Arc::new(
        Client::builder().timeout(Duration::from_secs(20))
        //.proxy(reqwest::Proxy::all(&format!("socks5://{}:{}", _proxy.ip, _proxy.port)).unwrap())
        .user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
        .build().unwrap()
    )).collect::<Vec<_>>();

    let number_of_spiders: usize = 500;

    let now = Instant::now();
    let counter = Arc::new(AtomicUsize::new(1));

    println!("Connecting to database...");
    unfold(connections.clone(), |pool| async {
        let records = {

            let connection = pool.get().await.unwrap();
            let url_records = UrlRecord::ready(&connection, number_of_spiders).unwrap();
            // let updated_records = UrlRecord::mark_as_processing(&connection, &url_records).unwrap();
            // assert!(updated_records <= url_records.len() );
            url_records
        };
        Some((iter(records), pool))
    })
    .for_each(move |block| async {
        block.for_each_concurrent(number_of_spiders, move |mut record| {

            // TODO: Remove this proxy if there are too many failed retries
            let client = clients.choose(&mut rng).unwrap().clone();
            let connections = connections.clone();
            let blacklist_reference_copy = blacklist_url_atomic_reference.clone();
            let counter_copy = counter.clone();
            // let mut status = UrlRecordStatus::Processed;

            async move {}

        }).await;
    }).await;    

        /*
                
        
                if (counter_copy.load(Ordering::Relaxed) as usize % 10) == 0 {
                    let req_per_sec = (counter_copy.load(Ordering::Relaxed) as f32) / (now.elapsed().as_secs() + 1) as f32;
                    println!("Seconds {} -- Items {} -- {} requests/s -- {} requests/min -- {} requests/h -- {} requests/day", 
                        counter_copy.load(Ordering::Relaxed), 
                        now.elapsed().as_secs(), 
                        req_per_sec, 
                        (req_per_sec * 60.0) as i64, 
                        (req_per_sec * 60.0 * 60.0) as i64, 
                        (req_per_sec * 60.0 * 60.0 * 24.0) as i64
                    );
                }
        
                async move { tokio::spawn(async move {
        
                    counter_copy.fetch_add(1 as usize, Ordering::Relaxed);
        
                    let request_response = client.get(record.data()).send().await;
                    let connection = connections.get().await.unwrap();
        
                    // Unpack response and mark as failed if cannot unpack
                    let response: reqwest::Response; 
                    match request_response {
                        Ok(v) => response = v,
                        Err(e) => {
                            // println!("E1 {:?}", e);
                            
                            record.set_status(UrlRecordStatus::Ready);
                            record.set_retries(record.retries() + 1);
                            /*
                            match record.save(&connection) {
                                Err(e) => {
                                    println!("E2 {:?}", e);
                                }
                                _ => (),
                            }
                            */
                            
                            return;
                        }
                    }
        
                    // If unsuccessful, mark as failed
                    if !response.status().is_success() {
        
                        record.set_status(UrlRecordStatus::Failed);
                        /*
                        match record.save(&connection) {
                            Err(e) => {
                                println!("E3 {:?}", e);
                            }
                            _ => (),
                        }
                        */
                        return;
                    }
        
                    // Extract string from HTML document
                    let document: std::string::String;
                    match response.text().await {
                        Ok(document_response) => document = document_response,
                        Err(err) => {
                            println!("E4 {:?}", err);
                            
                            record.set_status(UrlRecordStatus::Failed);
                            /*
                            match record.save(&connection) {
                                Err(e) => {
                                    println!("E5 {:?}", e);
                                }
                                _ => (),
                            }
                            */
                            
                            return;
                        }
                    }
        
                    // A bunch of logic to extract the links
                    let mut collected_urls: HashSet<Url> = HashSet::new();
        
                    let base_url: String = record.data().to_string();
                    let parsed_base_url: Url = Url::parse(&base_url).unwrap();
                    let base_host = parsed_base_url.host_str().unwrap();
                    let base_origin_string: String = parsed_base_url.scheme().to_string() + &"://".to_string() + &base_host;
                    let parsed_base_origin: Url = Url::parse(&base_origin_string).unwrap();
        
                    // Parse all href links from the response 
                    Document::from(document.as_str())
                    .find(Name("a"))
                    .filter_map(|n| n.attr("href"))
                    .for_each(|x| {
                        
                        // If no base-url, include it
                        let mut current_url: String = x.to_string();
        
                        // TODO take out all utm parameters (see python code) 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'
                        match current_url.chars().next() {
                            Some(v) => {
                                if v == '/' || (current_url.len() > 3 && &current_url[..4] != "http") {
                                    current_url = parsed_base_origin.join(current_url.as_str()).unwrap().to_string();
                                } 
                                if v != '#' && base_url != "javascript:void(0)" {
                                    // Turn x into a URL object
                                    match Url::parse(&current_url) {
                                        Ok(parsed_url) => {
                                            let normalized_url = normalize(parsed_url);
                                            match normalized_url {
                                                Ok(parsed_url) => {
                                                    collected_urls.insert(parsed_url);
                                                },
                                                Err(err) => { println!("E5.1{:?}", err); }
                                            };
                                        },
                                        Err(err) => { println!("E6 {:?}", err); }
                                    };
                                }
                            },
                            _ => (),
                        }
                    });
        
                    // For all collected urls, insert them into the database
                    for url in &collected_urls {
        
                        let mut status: UrlRecordStatus = UrlRecordStatus::Ready;
                        let depth;
                        match url.host_str() {
                            None => (),
                            Some(parsed_domain) => {
                                        
                                // Maybe apply faster logic somehow
                                if blacklist_reference_copy.contains(&parsed_domain.to_owned()) || url.cannot_be_a_base() {
                                    status = UrlRecordStatus::Ignored;
                                }
                                depth = record.depth() + 1;
            
                                // Save all newly found URLs into the database
                                /*
                                let url_record_response = UrlRecord::get_or_insert(&connection, url.as_str(), status, depth as i32);
                                match url_record_response {
                                    Ok(url_record) => {
                                        // Save all newly found URLs into the database queue
                                        let insert_result = UrlReferralRecord::get_or_insert(&connection, record.id(), url_record.id(), 1);
                                        match insert_result {
                                            Ok(_) => (),
                                            Err(e) => {
                                                // TODO: Mark as failed
                                                println!("Insert URL Referral Record");
                                                println!("E7 {:?}", e);
                                            }
                                        }
                                    },
                                    Err(e) => {
                                        // TODO: Mark as failed
                                        println!("Get or Insert URL Record");
                                        println!("E8 {:?}", e);                        
                                    }
                                }
                                */
                            }
                        }
                    };
        
                    // Save markdown to database // Insert should always call the "0" status (a python script later will modify this)
                    /*
                    let insert_result = MarkupRecord::get_or_insert(&connection, record.id(), &document.to_string(), 0 as i16);
                    match insert_result {
                        Ok(_) => {
                            record.set_status(UrlRecordStatus::Processed);
                            match record.save(&connection) {
                                Ok(()) => {
                                    counter_copy.fetch_add(1 as usize, Ordering::Relaxed);
                                },
                                Err(e) => {
                                    println!("E9 {:?}", e);
                                }
                            }
                        },
                        Err(e) => {
                            println!("Failed Insert Markup Record");
                            println!("E10 {:?}", e);
                            record.set_status(UrlRecordStatus::Failed);
                            match record.save(&connection) {
                                Ok(()) => (),
                                Err(e) => {
                                    println!("E11 {:?}", e);
                                }
                            }
                        }
                    };*/
                    ()
                }).await.ok();
                };
            };
        });
        */
}

pub async fn main<'a>(globals: &ArgMatches<'a>, args: &ArgMatches<'a>) {
    println!("Starting run...");
    run(globals, args).await;
}
