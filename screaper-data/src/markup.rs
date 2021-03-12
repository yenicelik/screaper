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

impl MarkupRecord {

    pub fn get_or_insert(
        connection: &PgConnection,
        raw: &str,
        status: i16
    ) -> QueryResult<Self> {
        diesel::insert_into(markup::table)
            .values((markup::raw.eq(raw), markup::status.eq(status as i16)))
            .on_conflict(markup::raw)
            // Update is required for return value
            .do_update()
            .set(markup::url_id.eq(markup::url_id))
            .returning(markup::all_columns)
            .get_result(connection)
    }
    
}
