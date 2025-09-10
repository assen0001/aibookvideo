/*
Source Database       : aibookvideo
Target Server Type    : MYSQL
Target Server Version : 50744
File Encoding         : 65001
Date: 2025-09-10 15:35:35
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for ai_booklist
-- ----------------------------
DROP TABLE IF EXISTS `ai_booklist`;
CREATE TABLE `ai_booklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '书单列表ID',
  `book_name` varchar(255) DEFAULT NULL COMMENT '书名',
  `book_author` varchar(255) DEFAULT NULL COMMENT '作者',
  `book_note` varchar(5000) DEFAULT NULL COMMENT '书籍简介',
  `book_supplement_prompt` varchar(255) DEFAULT NULL COMMENT '补充性提示词',
  `book_content` varchar(5000) DEFAULT NULL COMMENT 'AI生成方案',
  `book_status` int(11) DEFAULT '0' COMMENT '0-待生成文案，1-已生成文案，2-已生成字幕，3-已生成语音，4-已生成图片，5-已图生视频 ，6-已完成',
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `sdxl_prompt_styler` varchar(255) DEFAULT NULL COMMENT '提示词样式',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for ai_imageslist
-- ----------------------------
DROP TABLE IF EXISTS `ai_imageslist`;
CREATE TABLE `ai_imageslist` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '图片列表ID',
  `book_id` int(11) DEFAULT NULL COMMENT '书单ID（关联ai_booklist.id）',
  `paragraph_initial` varchar(5000) DEFAULT NULL COMMENT '段落',
  `paragraph_prompt_cn` varchar(5000) DEFAULT NULL COMMENT '段落提示词（中文）',
  `paragraph_prompt_en` varchar(5000) DEFAULT NULL COMMENT '段落提示词（英文）',
  `paragraph_status` int(11) DEFAULT '0' COMMENT '段落状态：0-待处理，1-已文生图',
  `images_url_01` varchar(255) DEFAULT NULL COMMENT '图片URL_01',
  `images_url_02` varchar(255) DEFAULT NULL COMMENT '图片URL_02',
  `images_url_03` varchar(255) DEFAULT NULL COMMENT '图片URL_03',
  `images_url_04` varchar(255) DEFAULT NULL COMMENT '图片URL_04',
  `images_status_01` int(11) DEFAULT '0' COMMENT '图片_状态_01：0-未选中，1-选中，2-图生视频',
  `images_status_02` int(11) DEFAULT '0' COMMENT '图片_状态_02：0-未选中，1-选中，2-图生视频',
  `images_status_03` int(11) DEFAULT '0' COMMENT '图片_状态_03：0-未选中，1-选中，2-图生视频',
  `images_status_04` int(11) DEFAULT '0' COMMENT '图片_状态_04：0-未选中，1-选中，2-图生视频',
  `images_supplement_prompt` varchar(255) DEFAULT NULL,
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `sdxl_prompt_styler` varchar(255) DEFAULT NULL COMMENT '提示词样式',
  `camera_movement` varchar(255) DEFAULT NULL COMMENT '运镜动作',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1704 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for ai_jobonline
-- ----------------------------
DROP TABLE IF EXISTS `ai_jobonline`;
CREATE TABLE `ai_jobonline` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `job_id` varchar(50) DEFAULT NULL COMMENT '任务编码',
  `job_name` varchar(50) DEFAULT NULL COMMENT '任务名称',
  `job_type` int(2) DEFAULT '0' COMMENT '任务类型：0-书单任务，1-方案，2-字幕，3-语音，4-图片，5-视频，6-合成',
  `job_status` int(2) DEFAULT '0' COMMENT '任务状态：0-新建，1-执行中，2-完成，3-暂停，4-失败，5-取消，6-排队中',
  `job_user` varchar(50) DEFAULT NULL COMMENT '任务所属用户',
  `book_id` int(11) DEFAULT NULL COMMENT '书单编号',
  `job_note` varchar(255) DEFAULT NULL COMMENT '任务备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `stop_time` datetime DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=369 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for ai_videolist
-- ----------------------------
DROP TABLE IF EXISTS `ai_videolist`;
CREATE TABLE `ai_videolist` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'videoID',
  `book_id` int(11) DEFAULT NULL COMMENT '书单ID（关联ai_booklist.id）',
  `images_id` int(11) DEFAULT NULL COMMENT '图片列表ID（关联ai_imageslist.id）',
  `images_url` varchar(255) DEFAULT NULL COMMENT '图片URL',
  `video_url` varchar(255) DEFAULT NULL COMMENT '视频URL',
  `video_status` int(11) DEFAULT '1' COMMENT '视频状态：0-未选中，1-选中',
  `createtime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1629 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for ai_videomerge
-- ----------------------------
DROP TABLE IF EXISTS `ai_videomerge`;
CREATE TABLE `ai_videomerge` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `book_id` int(11) DEFAULT NULL COMMENT '书单ID',
  `videomerge_url` varchar(255) DEFAULT NULL COMMENT '合成视频地址',
  `bilibili_url` varchar(255) DEFAULT NULL COMMENT 'B站视频URL',
  `video_status` int(11) DEFAULT '0' COMMENT '视频状态：0-已合成，1-已发布',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '合成时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for ai_voicelist
-- ----------------------------
DROP TABLE IF EXISTS `ai_voicelist`;
CREATE TABLE `ai_voicelist` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `book_id` int(11) DEFAULT NULL,
  `images_id` int(11) DEFAULT NULL,
  `voice_filename` varchar(255) DEFAULT NULL COMMENT '语音URL',
  `voice_status` int(11) DEFAULT '1' COMMENT '语音状态：0-未选中，1-已选中',
  `start_time` int(11) DEFAULT NULL COMMENT '开始时间（毫秒）',
  `duration` int(11) DEFAULT NULL COMMENT '时长（毫秒）',
  `end_time` int(11) DEFAULT NULL COMMENT '结束时间（毫秒）',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=599 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for ai_voicemerge
-- ----------------------------
DROP TABLE IF EXISTS `ai_voicemerge`;
CREATE TABLE `ai_voicemerge` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `book_id` int(11) DEFAULT NULL COMMENT '书单ID',
  `voice_url` varchar(255) DEFAULT NULL COMMENT '语音URL',
  `voice_status` int(11) DEFAULT '1' COMMENT '语音状态：0-未选中，1-已选中',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8;
