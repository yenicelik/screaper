use crate::schema::url_referral;

use chrono::NaiveDateTime;
use diesel::{
    pg::PgConnection,
    Connection, ExpressionMethods, Insertable, QueryResult, Queryable, RunQueryDsl,
};

#[derive(Debug, Queryable, Insertable)]
#[table_name = "url_referral"]
pub struct UrlReferralRecord {
    pub referrer_id: i32,
    pub referee_id: i32,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub count: i32,
}
