use crate::schema::markup;

use chrono::NaiveDateTime;
use diesel::{
    pg::PgConnection, Connection, ExpressionMethods, Insertable, QueryResult, Queryable,
    RunQueryDsl,
};

#[derive(Debug, Queryable, Insertable)]
#[table_name = "markup"]
pub struct MarkupRecord {
    pub url_id: i32,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub raw: String,
    pub status: i16,
}
