use crate::schema::markup;

use chrono::NaiveDateTime;
use diesel::{
    pg::PgConnection, Connection, ExpressionMethods, Insertable, QueryResult, Queryable,
    RunQueryDsl,
};

#[derive(Debug, Insertable)]
#[table_name = "markup"]
pub struct PartialMarkupRecord {
    pub url_id: i32,
    pub raw: String,
}

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

    pub fn batch_insert(
        connection: &PgConnection,
        partial_markup_records: Vec<PartialMarkupRecord>,
    ) -> QueryResult<usize> {
        diesel::insert_into(markup::table)
            .values(&partial_markup_records)
            .on_conflict(markup::url_id)
            .do_update()
            .set(markup::raw.eq(markup::raw))
            .returning(markup::all_columns)
            .execute(connection)
    }

    pub fn insert(
        connection: &PgConnection,
        url_id: i32,
        raw: &str,
        status: i16,
    ) -> QueryResult<usize> {
        diesel::insert_into(markup::table)
            .values((
                markup::url_id.eq(url_id),
                markup::raw.eq(raw),
                markup::status.eq(status as i16),
            ))
            .on_conflict(markup::url_id)
            // Update is required for return value
            .do_update()
            .set(markup::raw.eq(markup::raw))
            .returning(markup::all_columns)
            .execute(connection)
    }
}
