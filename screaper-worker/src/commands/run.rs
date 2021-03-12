use std::{sync::Arc, thread};

use clap::{App, Arg, ArgMatches, SubCommand};
use deadpool::{
    managed::{Pool as ManagedPool, RecycleResult},
    unmanaged::Pool as UnmanagedPool,
};
use futures::future::{FutureExt, TryFutureExt};
use futures::stream::{iter, repeat_with, unfold, StreamExt};
use regex::Regex;
use reqwest::{Client, Error as ReqwestError};
use serde::Deserialize;
use rand::thread_rng;
use rand::seq::SliceRandom;

use screaper_data::{Connection, ConnectionError, UrlRecord};

fn is_number(string: String) -> Result<(), String> {
    let regex = Regex::new(r"^[0-9]+$").unwrap();

    if regex.is_match(&string) {
        Ok(())
    } else {
        Err("the provided value must be a valid number".to_owned())
    }
}

pub fn app() -> App<'static, 'static> {
    SubCommand::with_name("run")
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Proxy {
    ip: String,
    port: usize,
    ping: usize,
    failed: bool,
    anonymity: String,
    working_count: usize,
    uptime: f32,
    recheck_count: usize,
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

    let mut rng = thread_rng();

    // `socks4` protocol currently unsupported by reqwest
    let clients = reqwest::get("https://www.proxyscan.io/api/proxy?last_check=3600&uptime=70&ping=500&limit=20&type=socks5").await.unwrap()
        .json::<Vec<Proxy>>().await.unwrap()
        .into_iter()
        .map(|proxy| Arc::new(Client::builder().proxy(reqwest::Proxy::all(&format!("socks5://{}:{}", proxy.ip, proxy.port)).unwrap()).build().unwrap()))
        .collect::<Vec<_>>();

    unfold(connections.clone(), |pool| async {
        let records = {
            let connection = pool.get().await.unwrap();
            UrlRecord::ready(&connection, 100).unwrap()
        };

        Some((iter(records), pool))
    })
    .flatten()
    .for_each(|record| {
        let client = clients.choose(&mut rng).unwrap().clone();
        let connections = connections.clone();

        async move {
            tokio::spawn(async move {
                println!("HI");

                record.set_status(UrlRecordStatus.from(1));
                record.save(connection);

                let failed = false;
                
                // If panic happens here, increase retry amount by one
                let response = client.get(record.data()).send().await.unwrap_or_else(|| {
                    record.set_retries(record.retries() + 1);
                    failed = true;
                });

                // If response code is not "OK", then set retries and continue
                if (response.status.is_success()) {
                    failed = true;
                }

                // Continue to next url if failed somehow
                if (failed) {
                    record.set_status(UrlRecordStatus.from(1));
                    record.save(connection);
                    return;
                }

                let document = response.text().await.unwrap();

                let connection = connections.get().await.unwrap();

                let collected_urls: HashMap<URL> = HashMap::new();

                // Parse all href links from the response 
                Document::from(response.as_str())
                .find(Name("a"))
                .filter_map(|n| n.attr("href"))
                .for_each(|x| {
                    println!("{}", x);
                    // Turn x into a URL object
                    let url = URL.parse(x);
                    // Normalize all links => there is this rust package that does ISO normalization
                    // TODO take out all utm parameters (see python code) 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'
                    url = url_normalize(url);
                    collected_urls.insert_into(url);
                })
                ;
                // TODO Also parse the rawtext for any strings that match the URL regex scheme

                // TODO: Parse all links extracted as regex from the response
                // Match the following regex in the document to extract additional links
                // check python code here: https://github.com/yenicelik/screaper/blob/rust/screaper/engine/markup_processor.py for more
                regex = "(?i)\b((?:(https|https)?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))";

                // For all collected urls, insert them into the database
                collected_urls.forall(|url| {

                    // Mark them as skipped if they are contained in this list
                    // mark the item if it is in this list as skipped https://github.com/yenicelik/screaper/blob/rust/notebooks/notebooks_20201223_popular_websites/popular_websites.yaml
                    let status: i16 = 0;
                    let depth: i32 = record.depth() + 1;

                    // Save all newly found URLs into the database
                    let url_record: UrlRecord = {
                        data: url.tostring(),
                        status: status,
                        retries: 0,
                        score: 0,
                        depth: depth,
                    }
                    // Insert markup record into database (Should this be done here, or elsewhere)
                    url_record.save(connection);
                    // Gotta get the id that was inputted?

                    // Save all newly found URLs into the database queue
                    // Increase count if record already exists
                    let url_: UrlReferralRecord = {
                        referrer_id: record.id(),
                        referee_id: url_record.id(),
                        count: 0,
                    }

                    // Save markdown to database 
                    let markup_record: MarkupRecord = {
                        raw: document
                        status: 0  // Insert should always call the "0" status (a python script later will modify this)
                    }
                    // TODO Insert markup record into database (Should this be done here, or elsewhere)
                    markup_record.save(connection);

                })

                record.set_status(UrlRecordStatus.from(2));
                record.save(connection);

                // This easily makes VSCode crash, perhaps do this later
                println!("{:?}", response.text().await.unwrap());
                panic!();

            })
            .await
            .ok();
        }
    })
    .await;
}
