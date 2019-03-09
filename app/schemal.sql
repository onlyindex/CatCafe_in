drop table if exists user;
drop table if exists post;
drop table if exists tag;
drop table if exists comment;


--清除所有表格重新新建表格


create table user (
  id integer  primary key autoincrement,
  username varchar(20) unique not null,
  email varchar (254) unique not null,
  password varchar(128) not null,
  location varchar(50) ,
  about_me text
);

create table post (
  id integer  primary key autoincrement ,
  title varchar(60) not null,
  body text  not null,
  author_id integer  not null,
  topic_id integer  not null,
  created datetime default datetime.utcnow,
  foreign key (author_id) references  user (id),
  foreign key (topic_id) references  tag (id)
);

create table tag  (
id integer primary key autoincrement ,
tagname varchar(30) unique not null
);

--令人纠结的评论

create table comment(
id integer primary key autoincrement ,
post_id integer not null ,
username integer  not null,
replied_id integer not null,

foreign key (replied_id) references  comment (id)
foreign key (replied_id) references  replied (id)

);




