


-- 用户表
--role：user =1：m
--user：role = 1：1
-- role_id是表user的外键
create table user (
  user_id integer  primary key autoincrement,
  username varchar(20) unique not null,
  email varchar (254) unique not null,
  password varchar(128) not null,
  about_me text,

  role_id not null,
  foreign key (role_id) references role(role_id)

);

--用户角色
create table role(
  role_id integer primary key  autoincrement ,
  role_name varchar(20) unique not null
);
--日志表
-- user：post = 1：m
-- post：user = 1:1
-- user_id是post的外键
-- post.author=user.user_id

create table post(
  post_id integer  primary key autoincrement ,
  post_title varchar(60) not null,
  post_body text  not null,
  post_timestamp  default current_timestamp,

  author_id integer not null ,
  foreign key (author_id) references  user (user_id)

);
--标签表
create table tag(
tag_id integer primary key autoincrement ,
tag_name varchar(30) unique not null
);

--日志标签表
-- post：tag = m：m
-- tag:post =m:m
create  table r_post_by_tag(
  r_id integer primary key autoincrement ,
  post_id integer not null ,
  tag_id integer not null ,

 foreign key (post_id) references post(post_id) ,
 foreign key (tag_id) references tag(tag_id)

);
--评论表 待升级成嵌套评论
--post：comment =1：m
--comment：post =1：1
--post_id是comment表的外键
--comment.reader_id = user.user_id
create table comment(
comment_id integer primary key autoincrement ,
comment_body text not null ,
comment_timestamp timestamp default current_timestamp,

reader_id integer not null ,
post_id integer not null ,
foreign key (reader_id) references  user (user_id),
foreign key(post_id) references post(post_id)
);


