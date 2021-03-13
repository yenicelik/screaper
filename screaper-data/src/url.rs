use crate::schema::url;

use chrono::{NaiveDate, NaiveDateTime};
use diesel::{
    pg::PgConnection, AsChangeset, ExpressionMethods, Insertable, QueryDsl, QueryResult, Queryable,
    RunQueryDsl,
};

#[repr(C)]
#[derive(Copy, Clone, Debug)]
pub enum UrlRecordStatus {
    Failed = -2,
    Ignored = -1,
    Ready = 0,
    Processing = 1,
    Processed = 2,
}

impl From<i16> for UrlRecordStatus {
    fn from(value: i16) -> Self {
        match value {
            -2 => UrlRecordStatus::Failed,
            -1 => UrlRecordStatus::Ignored,
            0 => UrlRecordStatus::Ready,
            1 => UrlRecordStatus::Processing,
            2 => UrlRecordStatus::Processed,
            _ => unreachable!("invalid url record status"),
        }
    }
}

#[derive(Clone, Debug, Queryable, Insertable, AsChangeset)]
#[table_name = "url"]
pub struct UrlRecord {
    pub id: i32,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub data: String, // Could this be a URL datatype?
    pub status: i16,
    pub retries: i32,
    pub score: i32,
    pub depth: i32,
}

impl UrlRecord {
    pub fn id(&self) -> i32 {
        self.id
    }

    pub fn created_at(&self) -> NaiveDateTime {
        self.created_at
    }

    pub fn updated_at(&self) -> NaiveDateTime {
        self.updated_at
    }

    pub fn data(&self) -> &String {
        &self.data
    }

    pub fn status(&self) -> UrlRecordStatus {
        self.status.into()
    }

    pub fn retries(&self) -> u32 {
        self.retries as u32
    }

    pub fn score(&self) -> u32 {
        self.score as u32
    }

    pub fn depth(&self) -> i32 {
        self.depth as i32
    }

    pub fn set_status(&mut self, status: UrlRecordStatus) {
        self.status = status as _;
    }

    pub fn set_retries(&mut self, retries: u32) {
        self.retries = retries as _;
    }

    pub fn set_score(&mut self, score: u32) {
        self.score = score as _;
    }

    pub fn set_depth(&mut self, depth: i32) {
        self.depth = depth as _;
    }
}

impl UrlRecord {

    pub fn get_or_insert(
        connection: &PgConnection,
        data: &str,
        status: UrlRecordStatus,
        depth: i32
    ) -> QueryResult<Self> {
        diesel::insert_into(url::table)
            .values((url::data.eq(data), url::status.eq(status as i16), url::depth.eq(depth as i32)))
            .on_conflict(url::data)
            // Update is required for return value
            .do_update()
            .set(url::id.eq(url::id))
            .returning(url::all_columns)
            .get_result(connection)
    }

    pub fn ready(connection: &PgConnection, max: usize) -> QueryResult<Vec<Self>> {
        url::table
            .filter(url::status.eq(UrlRecordStatus::Ready as i16))
            // TODO: Increase retries counter
            .limit(max as _)
            .load::<UrlRecord>(connection)
    }

    pub fn save(&mut self, connection: &PgConnection) -> QueryResult<()> {
        diesel::update(url::table)
            .set(&*self)
            .returning(url::all_columns)
            .get_result(connection)
            .map(|updated| {
                *self = updated;
            })
    }
}
