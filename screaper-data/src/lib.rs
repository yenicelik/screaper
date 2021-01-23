#[macro_use]
extern crate diesel;

mod schema;

mod markup;
mod url;
mod url_referral;

pub use markup::*;
pub use url::*;
pub use url_referral::*;

pub fn connection(url: &str) -> Result<Connection, ConnectionError> {
    use diesel::Connection as _;
    Connection::establish(url)
}

pub type Connection = diesel::PgConnection;
pub type ConnectionError = diesel::ConnectionError;
