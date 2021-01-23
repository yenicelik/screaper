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
                let response = client.get(record.data()).send().await.unwrap();

                let connection = connections.get().await.unwrap();

                println!("{:?}", response.text().await.unwrap());

                panic!();
            })
            .await
            .ok();
        }
    })
    .await;
}
