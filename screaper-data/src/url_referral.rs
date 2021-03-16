use crate::schema::url_referral;
use crate::url::UrlRecord;

use chrono::NaiveDateTime;
use diesel::{
    pg::PgConnection,
    Connection, ExpressionMethods, Associations, Identifiable, Insertable, QueryResult, Queryable, RunQueryDsl,
};


pub struct PartialUrlReferralRecord {
    pub referrer_id: i32,
    pub referee_data: String // Could this be a URL datatype?
}

#[derive(Debug, Insertable)]
#[table_name = "url_referral"]
pub struct PartialInsertableUrlReferralRecord {
    pub referrer_id: i32,
    pub referee_id: i32
}

// Identifiable
#[derive(Debug, Queryable, Associations, Insertable)]
// #[belongs_to(Url, foreign_key = "referrer_id", foreign_key = "referee_id")]
#[table_name = "url_referral"]
pub struct UrlReferralRecord {
    pub referrer_id: i32,
    pub referee_id: i32,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub count: i32,
}

impl UrlReferralRecord {

    pub fn batch_insert(
        connection: &PgConnection,
        partial_url_referral_records: Vec<PartialInsertableUrlReferralRecord>
    ) -> QueryResult<usize> {
        diesel::insert_into(url_referral::table)
            .values(&partial_url_referral_records)
            .on_conflict((url_referral::referrer_id, url_referral::referee_id))
            .do_update()
            .set(url_referral::count.eq(url_referral::count + 1))
            .returning(url_referral::all_columns)
            .execute(connection)
    }

    pub fn insert(
        connection: &PgConnection,
        referrer_id: i32,
        referee_id: i32,
        count: i32
    ) -> QueryResult<usize> {
        diesel::insert_into(url_referral::table)
            .values(
                (
                    url_referral::referrer_id.eq(referrer_id), 
                    url_referral::referee_id.eq(referee_id), 
                    url_referral::count.eq(count)
                )
            )
            // If the pair referred id and referee id is conflict
            .on_conflict(
                (url_referral::referrer_id, url_referral::referee_id)
            )
            // Update is required for return value
            .do_update()
            // if existent, increase count 
            .set(url_referral::count.eq(url_referral::count + 1))
            .returning(url_referral::all_columns)
            .execute(connection)
    }
    
}