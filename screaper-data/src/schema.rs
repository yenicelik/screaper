table! {
    markup (url_id) {
        url_id -> Int4,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        raw -> Text,
        // processed -> Nullable<Text>,
        status -> Int2,
    }
}

table! {
    refinery_schema_history (version) {
        version -> Int4,
        name -> Nullable<Varchar>,
        applied_on -> Nullable<Varchar>,
        checksum -> Nullable<Varchar>,
    }
}

table! {
    url (id) {
        id -> Int4,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        data -> Text,
        status -> Int2,
        retries -> Int4,
        score -> Int4,
        depth -> Int4,
    }
}

table! {
    url_referral (referrer_id, referee_id) {
        referrer_id -> Int4,
        referee_id -> Int4,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        count -> Int4,
    }
}

joinable!(markup -> url (url_id));

allow_tables_to_appear_in_same_query!(
    markup,
    refinery_schema_history,
    url,
    url_referral,
);
