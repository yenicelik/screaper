use clap::{App, Arg, ArgMatches, SubCommand};
use futures::stream::{iter, StreamExt};
use regex::Regex;

use screaper_data::{UrlRecord, UrlRecordStatus};

fn is_url(string: String) -> Result<(), String> {
    let regex = Regex::new(r"^https?://(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$").unwrap();

    if regex.is_match(&string) {
        Ok(())
    } else {
        Err("provided value must be a valid url (including protocol)".to_owned())
    }
}

pub fn app() -> App<'static, 'static> {
    SubCommand::with_name("seed").about("add seed values").arg(
        Arg::with_name("urls")
            .required(true)
            .multiple(true)
            .help("url to add as seed")
            .validator(is_url),
    )
}

pub async fn main<'a>(globals: &ArgMatches<'a>, args: &ArgMatches<'a>) {
    let connection = screaper_data::connection(&globals.value_of("database_url").unwrap()).unwrap();

    args.values_of("urls").unwrap().for_each(|url| {
        UrlRecord::get_or_insert(&connection, url, UrlRecordStatus::Ready, -1).unwrap();
    });
}
