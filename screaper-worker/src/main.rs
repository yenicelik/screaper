use clap::{crate_authors, crate_description, crate_version, App, Arg};

#[tokio::main(flavor = "multi_thread")]
async fn main() {
    let matches = App::new("screaper")
        .version(crate_version!())
        .author(crate_authors!())
        .about(crate_description!())
        .arg(
            Arg::with_name("database_url")
                .global(true)
                .env("DATABASE_URL")
                .long("database-url"),
        )
        .subcommand(screaper_worker::commands::seed::app())
        .subcommand(screaper_worker::commands::run::app())
        .get_matches();

    matches.value_of("database_url").expect("a database url is required");

    if let Some(args) = matches.subcommand_matches("seed") {
        screaper_worker::commands::seed::main(&matches, args).await;
    } else if let Some(args) = matches.subcommand_matches("run") {
        screaper_worker::commands::run::main(&matches, args).await;
    }
}
