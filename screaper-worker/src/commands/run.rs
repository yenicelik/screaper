use std::{sync::Arc, thread, time::Duration, collections::HashSet};

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
    let clients = proxyResponse.proxies.into_iter().filter(|proxy| proxy.google_error == "no").map(|proxy| Arc::new(
        Client::builder().timeout(Duration::from_secs(20))
        .user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
        .build().unwrap()
    )).collect::<Vec<_>>();
    // let clients = proxyResponse.proxies.into_iter().filter(|proxy| proxy.google_error == "no").map(|proxy| Arc::new(Client::builder().timeout(Duration::from_secs(20)).proxy(reqwest::Proxy::all(&format!("socks5://{}:{}", proxy.ip, proxy.port)).unwrap()).build().unwrap())).collect::<Vec<_>>();

    println!("Connecting to database...");
    unfold(connections.clone(), |pool| async {
        let records = {
            let connection = pool.get().await.unwrap();

            // Only get items that are not being processed rn

            UrlRecord::ready(&connection, 100).unwrap()
        };
        println!("Connection successful");
        Some((iter(records), pool))

    })
    .flatten()
    .for_each_concurrent(3, |mut record| {
        let client = clients.choose(&mut rng).unwrap().clone();
        let connections = connections.clone();
        let blacklist_reference_copy = blacklist_url_atomic_reference.clone();

        async move {
            tokio::spawn(async move {
                println!("HI");

                let connection = connections.get().await.unwrap();

                record.set_status(UrlRecordStatus::Processing);
                let insert_result = record.save(&connection);
                println!("{:?}", insert_result);

                let mut failed = false;
                
                println!("Making request");
                // If panic happens here, increase retry amount by one
                let response = client.get(record.data()).send().await.unwrap();
                println!("Made request");
                /*.unwrap_or_else(|e| {
                    record.set_retries(record.retries() + 1);
                    failed = true;
                    // println!(e);
                    // TODO: Spawn an empty response? What else...
                });*/

                // If response code is not "OK", then set retries and continue
                if (!response.status().is_success()) {
                    failed = true;
                }

                // Continue to next url if failed somehow
                if (failed) {
                    println!("failed");
                    println!("{:?}", response.text().await.unwrap());
                    record.set_status(UrlRecordStatus::Failed);
                    record.save(&connection);
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
                                current_url = base_url.clone() + &current_url;
                            }

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
                    // Maybe apply faster logic somehow
                    if (blacklist_reference_copy.contains(&url.as_str().to_owned())) {
                        status = UrlRecordStatus::Ignored;
                    } else {
                        status = UrlRecordStatus::Ready;
                    }
                    let depth = record.depth() + 1;

                    // Save all newly found URLs into the database
                    let url_record: UrlRecord = UrlRecord::get_or_insert(&connection, url.as_str(), status, depth as i32).unwrap();

                    // Save all newly found URLs into the database queue
                    // Increase count if record already exists
                    UrlReferralRecord::get_or_insert(&connection, record.id(), url_record.id(), 1);

                    // Save markdown to database // Insert should always call the "0" status (a python script later will modify this)
                    MarkupRecord::get_or_insert(&connection, &document.to_string(), 0 as i16);

                }

                record.set_status(UrlRecordStatus::Processed);
                record.save(&connection);

                // This easily makes VSCode crash, perhaps do this later
                // println!("{:?}", response.text().await.unwrap());
                panic!();

            })
            .await
            .ok();
        }
    })
    .await;
}
