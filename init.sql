
-- sequence
create sequence book_id_seq start 1 increment 1;
create sequence user_id_seq start 1 increment 1;

-- table
create table books (
    id int primary key default nextval('book_id_seq'),
    title varchar(255) not null,
    author varchar(100) not null,
    publish_date date not null,
    isbn varchar(15) not null,
    price numeric(10, 2) not null,
    is_deleted boolean not null,
    created_at timestamp default CURRENT_TIMESTAMP,
    updated_at timestamp
);
create unique index books_title_author_idx on books (title, author);

create table users (
    id int primary key default nextval('user_id_seq'),
    email varchar(100) unique not null,
    hashed_password varchar(255) not null,
    created_at timestamp default CURRENT_TIMESTAMP,
    updated_at timestamp
);