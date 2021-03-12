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
    
    pub fn save(&mut self, connection: &PgConnection) -> QueryResult<()> {
        diesel::update(markup::table)
            .set(&*self)
            .returning(markup::all_columns)
            .get_result(connection)
            .map(|updated| {
                *self = updated;
            })
    }
}
