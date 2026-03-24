1 API使用规范
本文中所列API支持明文和加密两种方式调用；加密调用方式及说明已经在本文附录中进行说明。

1.1 调用步骤
调用方可以通过阳光云开放API，从阳光云获取需要的电站信息和设备信息等。调用方首先根据阳光云提供的用户账号和密码调用/openapi/login接口进行身份认证，得到授权的token，在token有效期（24小时）之内进行其他接口的调用。

说明：在token有效期内，每使用该token调用一次接口，该token的有效期会自动恢复为24小时,调用方无需每次调用都获取新的token。

1.2 错误码定义
详见 附录2：API错误码定义

1.3 约束说明
（1）本文中所有接口中使用到的用户账号、appkey等相关信息全部严格按照《阳光电源iSolarCloud云平台接口开放API-授权书说明》中的规定进行调用并获取相关数据；

（2）Http请求全是以POST的方式进行；

（3）调用平台所有的服务都需要传入平台授权的appkey，对应请求体参数名称为：appkey；

（4）调用每个API都需要传入token进行身份的校验，对应请求体参数名称为：token，[/openapi/login接口除外]；

（5）以下为请求头里面的相关参数说明：

参数名	类型	长度	描述	是否必传
Content-Type	String	32	传入：application/json;charset=UTF-8	是
sys_code	String	11	系统编码：第三方调用传入901	是
x-access-key	String	32	阳光云分配的access_key	是
x-random-secret-key	String	16	本次请求的密钥，明文长度16位，需经过RSA加密后传输， 出参使用该明文密钥进行AES解密， 加密请求时传入如何获取x-random-secret-key	否
（6）请求体里面需要传入以下公共参数，以下公共入参在每个API定义里面不再一一列出。

参数名	类型	长度	描述	是否必传
appkey	String	32	授权码，必传 (接口给客户端系统分配的appkey)。	是
token	String	40	token (登陆成功后API返回的token)	是
lang	String	6	语言（不传则默认简体中文）：
简体中文：_zh_CN
英文：_en_US
日本语：_ja_JP
西班牙语：_es_ES
德语：_de_DE
巴西葡萄牙语：_pt_BR
葡萄牙语：_pt_BR
法语：_fr_FR
意大利语：_it_IT
韩语：_ko_KR
荷兰语：_nl_NL
波兰语：_pl_PL
越南语：_vi_VN
繁体中文：_zh_TW	否
api_key_param	Map		其他公共参数	否
timestamp	String		格林威治UNIX时间戳（毫秒级）	否
nonce	String	32	数字和字母组成的32位的随机字符串	否
（7）以下公共出参在每个API定义中不再一一列出。

参数名	类型	长度	描述
req_serial_num	String	32	请求序列号
result_code	String	11	错误码
result_msg	String	100	提示信息
result_data	Object		返回数据： 支持类型：String，Map，List等，具体数据格式请参照本文对应的API出参定义，本文中定义的出参数据都在该result_data参数下
（8） API 域名：在调用API文档中的接口时，请选择以下阳光电源提供的对应站点的API域名： 

中国站：https://gateway.isolarcloud.com/

国际站：https://gateway.isolarcloud.com.hk/

欧洲站：https://gateway.isolarcloud.eu/

澳洲站：https://augateway.isolarcloud.com/




用户登陆
Post
/openapi/login

用户登陆
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
user_account
String
是
sungrowUser
用户账户
user_password
String
是
pw111111
用户密码
{
  "user_account":"polana7333@tsderp.com",
	"user_password":"1qaz@WSX"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240920d9184e7fa2e9a031e5e96f5b
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.disable_time
String
2024-11-27 13:44:45
账号锁定日期
result_data.email
String
yang@163.com
用户邮箱地址
result_data.err_times
String
0
密码出错次数
result_data.language
String
Chinese
用户语言
result_data.login_state
String
1
登陆状态： -1：用户账号不存在 0：密码错误 1：登录成功 2：密码输入错误导致账户锁定 5：该账号被管理员锁定
result_data.mobile_tel
String
13155366666
用户手机号码
result_data.token
String
503093_fce7a5839e6c46f998952d55c0384774
认证成功后返回token
result_data.user_account
String
Autotest
用户账号
result_data.user_id
String
503093
用户id
result_data.user_master_org_id
String
527815
用户组织id
result_data.user_master_org_name
String
Brenergie BV
用户组织名称
result_data.user_name
String
org-bjrdeen0qi
用户昵称
result_data.country_name
String
China
国家名
result_data.country_id
String
1
国家id
2.1 成功示例
{
	"req_serial_num":"202411133cea4e6c8ef73fd79f8f82a7",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"user_master_org_id":"530435",
		"mobile_tel":null,
		"user_name":null,
		"language":"English",
		"token":"505120_2a62bd4e737e4e8fabc9caaa97f032c6",
		"err_times":"0",
		"user_id":"505120",
		"login_state":"1",
		"disable_time":null,
		"country_name":"Germany",
		"user_account":"bwq770s46t",
		"user_master_org_name":"M-wise",
		"email":"polana7333@tsderp.com",
		"country_id":"50"
	}
}
2.2 失败示例
{
	"req_serial_num": "202411133cea4e6c8ef73fd79f8f82a7",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"login_state": "-1",
		"msg": "账号不存在"
	}
}
2.3 错误码
错误码
描述
-1
用户账号不存在
0
密码错误
1
登录成功
2
密码输入错误导致账号锁定
5
该账号被管理员锁定


电站分享
Post
/openapi/sharePsBySN

通过电站分享授权人账号、电站下某台设备的SN、接受分享的用户账号进行电站的分享。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
sn
String
是
A2460402220
设备S/N
accept_user_account
String
是
18311475904
接受电站分享的用户的账号（接受分享）
owner_user_account
String
是
18268826725
发起电站分享的用户的账号（电站业主）
share_type
String
否
1
添加的渠道合作方权限类型： 1：浏览权限 2：管理权限 默认值：2
{
	"accept_user_account": "18311475904",
	"token": "598226_bfc7584826be4405b4a39cd9de0d827b",
	"appkey": "5E4BFC5877FD2052260212532686F2DD",
	"sn": "A2460402220",
	"owner_user_account": "18268826725"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
0dffcf2c57a142f69aba778622bf44d6
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.code
String
1
操作结果编码： 1：分享成功 2：根据设备sn未查询到对应电站 3：发起分享的用户不存在 4：接受分享的用户不存在 5：设备sn对应的电站不属于分享人，无法分享 6：设备sn对应的电站已经在接受分享的用户下，无需再分享 12：不支持的电站分享类型
2.1 成功示例
{
	"req_serial_num":"20241126c0e94d10b9f0be836c891356",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"code":"1"
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}

电站解除分享
Post
/openapi/releasePsSharing

业主对自己分享的电站进行解除分享，或接受电站分享的用户发起的解除分享。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_id_list
List
是
[475020,446426,338112,363380]
电站ps_id集合
release_type
String
是
2
类型： 1：业主主动解除对accept_user_account的分享； 2：接受电站分享的用户发起的解除分享； 默认2
accept_user_account
String
是
autotest
接受电站分享的用户账号；release_type等于1时必传
{
	"ps_id_list":[
		475020,
		446426,
		338112,
		363380,
		476422
	]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202411289d684681bbf720caa37c51ff
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.code
String
1
结果编码： 1：解除分享成功； 2：接受电站分享的用户账号不存在； 3：电站不在接受电站分享的用户下，无法解除分享；
2.1 成功示例
{
	"req_serial_num":"202411289d684681bbf720caa37c51ff",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"result_code":1
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}

电站添加渠道合作方
Post
/openapi/shareMyPs

将某用户添加为电站的渠道合作方，支持批量操作。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_id_list
List
是
[475020,446426,338112,363380]
电站ps_id集合
user_email
String
否
155147263@gmail.com
被添加人邮箱 账号、邮箱、手机号码三者最多只能传一项
share_type
String
是
1
添加的渠道合作方权限类型： 1：浏览权限 2：管理权限
is_channel_partner
String
是
1
添加为渠道合作方，固定传1
{
	"is_channel_partner": 1,
	"user_email": "163568367@gmail.com",
	"ps_id_list": [
		475020,
		446426,
		338112,
		363380,
		476422
	],
	"share_type": "1"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241128d9c54e20a843bd2d35e08844
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.result_code
Integer
1
操作结果编码： 0: 未知原因导致失败，请联系管理员； 1:成功； 2: ps_id_list集合入参不正确；传入的ps_id_list中有重复电站或者有不存在的ps_id,或者有ps_id不属于操作用户所有； 4:只能传入一项被添加人信息； 5:渠道/合作方已存在； 6:此用户已存在浏览或管理当前电站的权限； 7:被操作的电站中有电站（管理权限）已经超过添加上限了； 8:此用户已存在浏览或管理当前电站的权限； 9:渠道/合作方已存在； 11: 被添加人不存在
2.1 成功示例
{
	"req_serial_num":"20241128feb24604b0611b56fc2b47c0",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"result_code":"1"
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


解除电站渠道合作方
Post
/openapi/cancelPsSharing

将电站的渠道合作方解除，支持批量操作。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_id_list
List
是
[475020,446426,338112,363380]
电站ps_id集合
share_type
String
是
2
添加的渠道合作方权限类型： 1：浏览权限 2：管理权限
is_channel_partner
String
是
1
添加为渠道合作方，固定传1
user_email
String
否
1536727388@gmail.com
被解除人邮箱 邮箱、手机号码需要传一项
user_mobile_tel
String
否
18562**6532
被解除人手机号码 邮箱、手机号码需要传一项
{
	"user_mobile_tel":"",
	"user_email":"1536727388@gmail.com",
	"ps_id_list":[
		475020,
		446426,
		338112,
		363380,
		476422
	],
	"is_channel_partner":"1",
	"share_type":"2",
	"user_id":"256154"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241126b2084df8b8db5f67e15bf908
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.result_code
Integer
1
操作结果编码： 1：解除成功 0：解除失败
2.1 成功示例
{
	"req_serial_num":"20241128feb24604b0611b56fc2b47c0",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"result_code":"1"
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}



通过逆变器sn和nmi新增电站渠道合作方
Post
/openapi/sharePowerStationBySnAndNmi

通过逆变器sn和nmi批量新增渠道合作方，最多传入50组数据，新增成功后会为电站业主和安装商发送一条通知邮件（只适用于澳洲）
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
list
List
是
--
sn与nmi集合，最多传入50组
list.sn
String
是
Y2232400010
逆变器sn
list.nmi
String
是
10989879072
NMI
{
	"list":[
		{
			"sn":"A2162500851",
			"nmi":"10989879073"
		},
		{
			"sn":"A2191001080",
			"nmi":"10989879074"
		},
		{
			"sn":"A2162500747",
			"nmi":"10989879075"
		},
		{
			"sn":"A21C0305600",
			"nmi":"10989879076"
		},
		{
			"sn":"A21A1515523",
			"nmi":"10989879077"
		},
		{
			"sn":"Y2232400010",
			"nmi":"10989879072"
		}
	]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241126953442bc9581ba16d069e336
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.success_list
List
--
新增成功列表
result_data.success_list.sn
String
A2462**0013
设备S/N
result_data.success_list.nmi
String
10989879074
NMI
result_data.illegal_list
List
--
失败列表
result_data.illegal_list.sn
String
A2162500851
设备S/N
result_data.illegal_list.nmi
String
10989879073
NMI
result_data.illegal_list.code
Integer
2
错误类型 0-传入参数sn,nmi是否为空 1-传入的sn或nmi重复 2-通过nmi与通过sn查询的电站不同 3-电站在该用户下电站已存在 4-nmi长度不能低于10
2.1 成功示例
{
	"req_serial_num":"20241126953442bc9581ba16d069e336",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"success_list":[],
		"illegal_list":[
			{
				"code":2,
				"sn":"A2162500851",
				"nmi":"10989879073"
			},
			{
				"code":2,
				"sn":"A2191001080",
				"nmi":"10989879074"
			},
			{
				"code":2,
				"sn":"A2162500747",
				"nmi":"10989879075"
			},
			{
				"code":2,
				"sn":"A21C0305600",
				"nmi":"10989879076"
			},
			{
				"code":2,
				"sn":"A21A1515523",
				"nmi":"10989879077"
			},
			{
				"code":2,
				"sn":"Y2232400010",
				"nmi":"10989879072"
			}
		]
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


电站列表信息查询
Post
/openapi/getPowerStationList

查询用户下电站列表信息或根据用户组织ID查询电站列表信息。如果找不到您需要的信息，可以通过该接口拿到电站的ps_id，调用"查询电站的实时数据接口"传入所需数据测点号获取
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_name
String
否
PlantA
电站名称(模糊查询)
ps_type
String
否
1,3,4,5,6,7,8
电站类型：（多个使用英文逗号隔开传入，默认查询所有） 1：地面电站 3：分布式光伏 4：户用光伏 5：户用储能 6：村级电站 7：分布式储能 8：扶贫电站 9：风能电站 10：地面储能电站 12：工商业储能电站
share_type
String
否
0,1,2
电站的分享类型： 1：查询具有浏览权限的分享电站 2：查询具有管理权限的分享电站 0：查询本人电站 多个类型使用逗号隔开传入，默认查询所有
valid_flag
String
否
1,3
需要查询的电站状态： （1：正常，2：停用, 3：接入中）如果不传该节点，则查询1状态的电站。 如果需要查询多个状态，使用逗号隔开。
org_id
String
否
527815
如果是根据组织id进行查询，则传入，对应login接口返回的 user_master_org_id出参
curPage
Integer
是
1
页码
size
Integer
是
10
每页大小
user_id
String
否
506574
用户id （用户必须是登录账号的下级）
is_self_built
Integer
否
0
是否自建电站0-全部 1-自建 默认0全部
{
	"curPage": 1,
	"size": 10
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
2022122373544aab92527faf91b7addc
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.pageList
List
--
分页数据
result_data.pageList.alarm_count
Integer
0
告警数量
result_data.pageList.build_status
Integer
2
电站建设状态 0：未建，1：在建 2：并网，3：拟建，4：未接入
result_data.pageList.co2_reduce
Map
--
今日CO₂减排
result_data.pageList.co2_reduce.unit
String
千克
数值单位
result_data.pageList.co2_reduce.value
String
0
数值
result_data.pageList.co2_reduce_total
Map
--
累计CO₂减排
result_data.pageList.co2_reduce_total.unit
String
Ton
数值单位
result_data.pageList.co2_reduce_total.value
String
661405
数值
result_data.pageList.co2_reduce_update_time
String
2024-11-14T16:00:50+08:00
今日co2减排最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.connect_type
Integer
1
并网类型：1：全额上网 2：自发自用，余电上网 3：自发自用，无馈网 4：离网
result_data.pageList.curr_power
Map
--
当前功率
result_data.pageList.curr_power.unit
String
TWp
数值单位
result_data.pageList.curr_power.value
String
5
数值
result_data.pageList.co2_reduce_total_update_time
String
2024-11-14T16:00:50+08:00
累计co2减排最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX<br>
result_data.pageList.curr_power_update_time
String
2024-11-14T16:00:50+08:00
当前功率最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.description
String
Rooftop power station
电站简介
result_data.pageList.equivalent_hour
Map
--
今日等效小时
result_data.pageList.equivalent_hour.unit
String
h
数值单位
result_data.pageList.equivalent_hour.value
String
8
数值
result_data.pageList.equivalent_hour_update_time
String
2024-11-14T16:00:50+08:00
今日等效小时最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.fault_count
Integer
0
故障数量
result_data.pageList.install_date
String
2022-11-07 15:37:40
建站时间 格式：yyyy-MM-dd HH:mm:ss
result_data.pageList.latitude
Num
41.69395123697499
经度
result_data.pageList.longitude
Num
123.18212151404492
维度
result_data.pageList.ps_current_time_zone
String
GMT+8
电站当前时区
result_data.pageList.ps_fault_status
Integer
3
电站故障状态，1：故障，2：告警，3 :正常
result_data.pageList.ps_id
Integer
729056
电站ID
result_data.pageList.ps_location
String
Longtu Rd, Shushan District, Hefei, Anhui, China
电站位置
result_data.pageList.ps_name
String
PlantA
电站名称
result_data.pageList.ps_status
Integer
0
电站状态 1：在线，0：离线
result_data.pageList.ps_type
Integer
4
电站类型：（多个使用英文逗号隔开传入，默认查询所有） 1：地面电站 3：分布式光伏 4：户用光伏 5：户用储能 6：村级电站 7：分布式储能 8：扶贫电站 9：风能电站 10：地面储能电站 12：工商业储能电站
result_data.pageList.share_type
String
0
电站的分享类型 1：分享类型（浏览权限） 2：分享类型（管理权限） 0：非分享电站（本人电站）
result_data.pageList.today_energy
Map
--
电站今日发电
result_data.pageList.today_energy.unit
String
kWh
数值单位
result_data.pageList.today_energy.value
String
11.77
数值
result_data.pageList.today_energy_update_time
String
2024-11-14T16:00:50+08:00
今日发电量最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.today_income
Map
--
电站今日收益<value,unit>（当电站为储能类型时，收益为储能收益）
result_data.pageList.today_income.unit
String
CNY
数值单位
result_data.pageList.today_income.value
String
11.77
数值
result_data.pageList.today_income_update_time
String
2024-11-14T16:00:50+08:00
今日收益最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.total_capcity
Map
--
总装机量
result_data.pageList.total_capcity.unit
String
kWp
数值单位
result_data.pageList.total_capcity.value
String
330
数值
result_data.pageList.total_capcity_update_time
String
2022-11-07T15:37:40+08:00
总装机量最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.total_energy
Map
--
电站累计发电
result_data.pageList.total_energy.unit
String
kWh
数值单位
result_data.pageList.total_energy.value
String
11.77
数值
result_data.pageList.total_energy_update_time
String
2024-11-14T16:00:50+08:00
电站累计发电量最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.total_income
Map
--
累计收益<value,unit>（当电站为储能类型时，收益为储能收益）
result_data.pageList.total_income.unit
String
CNY
数值单位
result_data.pageList.total_income.value
String
11.77
数值
result_data.pageList.total_income_update_time
String
2024-11-14T16:00:50+08:00
累计收益最后更新时间 格式：yyyy-MM-dd'T'HH:mm:ssXXX
result_data.pageList.valid_flag
Integer
3
电站状态，1：正常，2：停用，3：接入中
result_data.pageList.province_name
String
AnHui
省
result_data.pageList.city_name
String
HeFei
市
result_data.pageList.district_name
String
Xicheng District
区
result_data.pageList.grid_connection_status
Integer
1
并网状态 1-已并网 0-未并网
result_data.pageList.grid_connection_time
Integer
20230303115625
并网时间
result_data.pageList.month_income_update_time
String
2024-11-14T16:00:50+08:00
当月收益更新时间
result_data.pageList.month_income
Map
--
当月收益（当电站为储能类型时，收益为储能收益）
result_data.pageList.month_income.unit
String
CNY
当月收益的单位
result_data.pageList.month_income.value
String
11.77
当月收益的值
result_data.pageList.year_income
Map
--
当年收益（当电站为储能类型时，收益为储能收益）
result_data.pageList.year_income.unit
String
CNY
当年收益的单位
result_data.pageList.year_income.value
String
11.77
当年收益的值
result_data.rowCount
String
1
记录数
2.1 成功示例
{
	"req_serial_num": "20241114f0ff469abf8502b5edb6a80f",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"pageList": [{
			"total_energy": {
				"unit": "度",
				"value": "381.6"
			},
			"alarm_count": 0,
			"latitude": null,
			"description": null,
			"total_income_update_time": "2024-11-14T16:00:50+08:00",
			"valid_flag": 1,
			"curr_power": {
				"unit": "W",
				"value": "358"
			},
			"ps_fault_status": 3,
			"district_name": "东城区",
			"co2_reduce_update_time": "2024-11-14T16:00:50+08:00",
			"city_name": "北京城区",
			"install_date": "2024-11-12 18:19:36",
			"build_status": 2,
			"today_energy_update_time": "2024-11-14T16:00:50+08:00",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


查询电站下设备列表
Post
/openapi/getDeviceList

根据电站ID查询电站下的设备列表。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_id
String
是
476178
电站ID
curPage
Integer
是
1
页码
size
Integer
是
10
每页大小
is_virtual_unit
String
否
0
是否是查询虚拟设备，1：查询的是虚拟设备，0：查询的是物理设备，默认为0，即表示查询物理设备，电站、并网点、单元都属于虚拟设备
device_type_list
List
否
--
设备类型列表，限定条件，为空，查看全部 如： 11：电站、 1：逆变器、 3：并网点、 17：单元。具体参考附录中的设备类型定义
rel_state
String
否
1
设备认领状态：0：未认领，1：认领
is_get_firmware_version
String
否
0
是否需要获取设备的固件版本信息 1：需要、0：不需要，默认不需要
{
	"curPage":1,
	"size":50,
	"ps_id":689661,
	"device_type_list":[
		1
	]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240829c4ba4ec98875ca2f1e7e8175
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.pageList
List
--
分页数据
result_data.pageList.chnnl_id
Integer
4
设备通道ID
result_data.pageList.communication_dev_sn
String
A2462**0013
设备对应的通信设备的SN
result_data.pageList.dev_fault_status
Integer
4
设备当前故障状态设备故障状态：1：故障，2：告警，4：正常
result_data.pageList.dev_status
String
1
设备当前在线离线状态：0：离线，1：在线
result_data.pageList.device_code
Integer
247
设备地址编码
result_data.pageList.device_model_code
String
iHomeManager
设备型号名称
result_data.pageList.device_model_id
Integer
367701
设备型号ID
result_data.pageList.device_name
String
Home Energy Manager3
设备名称
result_data.pageList.device_sn
String
A2462**0013
设备SN
result_data.pageList.device_type
Integer
64
设备类型编码
result_data.pageList.factory_name
String
Sunshine Power Co., Ltd
生产厂家名
result_data.pageList.ps_id
Integer
473465
电站ID
result_data.pageList.ps_key
String
7006*6130_64_247_1
设备的ps_key(查询设备数据需要用到)
result_data.pageList.rel_state
Integer
1
设备认领状态：0：未认领，1：认领
result_data.pageList.type_name
String
Home Energy Manager
设备类型名称
result_data.pageList.uuid
Integer
2024**5175
设备UUID
result_data.pageList.rel_time
String
--
设备认领时间
result_data.pageList.firmware_version_info
Map
--
设备的固件版本信息
result_data.pageList.firmware_version_info.bat_version
String
SBRBCU-S_22011.01.22
电池管理系统单板版本号
result_data.pageList.firmware_version_info.lcd_version
String
SAPPHIRE-H_01011.31.50
逆变器ARM软件版本号
result_data.pageList.firmware_version_info.mdsp_version
String
SAPPHIRE-H_03011.31.46
主DSP版本
result_data.pageList.firmware_version_info.sdsp_version
String
SUBCTL-S_04011.01.01
辅DSP版本
result_data.pageList.firmware_version_info.pvd_version
String
WINET-SV200.001.00.P023
组串检测板软件版本号
result_data.pageList.firmware_version_info.cpld_version
String
WINET-SV200.001.00.P023
CPLD固件版本号
result_data.pageList.firmware_version_info.temp_version
String
WINET-SV200.001.00.P023
温度板版本号
result_data.pageList.firmware_version_info.m_version
String
WINET-SV200.001.00.P023
通信设备软件版本号
result_data.pageList.firmware_version_info.system_version
String
WINET-SV200.001.00.P023
通信设备硬件平台版本号
result_data.rowCount
Integer
7
记录数
2.1 成功示例
{
	"req_serial_num":"202411277d7c4909868d4d9ef4c2ba61",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"pageList":[
			{
				"chnnl_id":5,
				"type_name":"逆变器",
				"ps_key":"689661_1_1_5",
				"device_sn":"A2262065536",
				"dev_status":"1",
				"device_type":1,
				"factory_name":"阳光电源股份有限公司",
				"uuid":3791641,
				"grid_connection_date":"2022-09-27 15:42:08",
				"device_name":"研发楼NB04",
				"dev_fault_status":4,
				"rel_state":1,
				"device_code":1,
				"ps_id":689661,
				"device_model_id":346856,
				"communication_dev_sn":"B2261882811",
				"device_model_code":"SG50CX-P2-CN"
			},
			{
				"chnnl_id":4,
				"type_name":"逆变器",
				"ps_key":"689661_1_1_4",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


查询电站的基本信息
Post
/openapi/getPowerStationDetail

查询电站的基本信息
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
sn
String
是
B2262720904
设备S/N
is_get_ps_remarks
String
是
1
是否获取电站的备注信息： 1：获取， 不传默认不获取
{
	"sn":"B2313140126",
	"is_get_ps_remarks":"1"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202212236d134e3386b3c49b66c966c5
请求序列号
result_code
String
1
错误码
result_data
Map
--
返回数据
result_data.alarm_count
Integer
0
告警数量
result_data.build_status
Integer
2
电站建设状态 0：未建，1：在建 2：并网，3：拟建，4：未接入
result_data.communication_dev_detail_list
List
--
电站的通信设备SN信息
result_data.communication_dev_detail_list.is_enable
Integer
1
SN状态：0：禁用，1：正常
result_data.communication_dev_detail_list.sn
String
A2462**0013
SN
result_data.connect_type
Integer
2
并网类型：1：全额上网 2：自发自用，余电上网 3：自发自用，无馈网 4：离网
result_data.description
String
Rooftop power station
电站简介
result_data.design_capacity
Integer
1000000
装机功率，单位为Wp
result_data.data_list.design_capacity_pcs
Integer
100
储能PCS功率
result_data.data_list.design_capacity_battery
Integer
100
储能电池容量
result_data.fault_count
Integer
0
故障数量
result_data.email
String
155147***64@gmail.com
业主用户的邮箱
result_data.install_date
String
2022-05-27 11:33:06
建站日期
result_data.latitude
Num
41.69395123697499
纬度
result_data.longitude
Num
123.18212151404492
电站经度
result_data.param_income_unit_name
String
CNY
电价单位
result_data.ps_current_time_zone
String
GMT+8
电站当前时区
result_data.ps_fault_status
Integer
3
电站故障状态，1：故障，2：告警，3 :正常
result_data.ps_id
Integer
974621
电站ID
result_data.ps_key
String
974621_11_0_0
电站的ps_key
result_data.ps_location
String
Longtu Rd, Shushan District, Hefei, Anhui, China
电站位置
result_data.ps_name
String
PlantA
电站名称
result_data.ps_price
String
0.001
电站当前每Wh的电价
result_data.ps_price_kwh
String
1
电站当前每kWh的电价
result_data.ps_remarks
Map
--
电站备注信息（入参is_get_ps_remarks为1时返回）
result_data.ps_status
Integer
0
电站状态 1：在线，0：离线
result_data.ps_type
Integer
3
电站类型：1：地面电站 3：分布式光伏 4：户用光伏 5：户用储能 6：村级电站 7：分布式储能 8：扶贫电站 9：风能电站 12：工商业储能
result_data.ps_type_name
String
Commercial PV
电站类型名称
result_data.share_type
String
2
电站的分享类型 1：分享类型（浏览权限）2：分享类型（管理权限）0：非分享电站（本人电站）
result_data.share_user_type
String
1
电站的分享人类型：1：业主分享2：安装商分享 其他：非分享电站
result_data.user_moble_tel
String
185736**246
业主用户手机号码
result_data.ps_remarks.remark1
String
Record rooftop power generation data for the power station
备注1
result_data.ps_remarks.remark2
String
Record rooftop power generation data for the power station
备注2
result_data.ps_remarks.remark3
String
Record rooftop power generation data for the power station
备注3
result_data.ps_remarks.remark4
String
Record rooftop power generation data for the power station
备注4
result_data.ps_remarks.remark5
String
Record rooftop power generation data for the power station
备注5
result_msg
String
success
提示信息
2.1 成功示例
{
	"req_serial_num":"20241127cf2a4725ac6ebd9e9caeab59",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"design_capacity":11000.0,
    "design_capacity_pcs": 200,
    "design_capacity_battery":1000,
		"alarm_count":0,
		"ps_key":"974621_11_0_0",
		"latitude":33.07597603786331,
		"description":null,
		"ps_price_kwh":"1",
		"ps_fault_status":3,
		"ps_type_name":"户用光伏",
		"build_status":2,
		"install_date":"2023-06-13 15:40:56",
		"ps_type":4,
		"email":null,
		"longitude":112.60275055975228,
		"param_income_unit_name":"元",
		"ps_price":"0.001",
		"ps_name":"李庚莲11kwB2313140126",
		"share_user_type":null,
		"ps_location":"河南省南阳市南召县太山庙乡张沟村核西组456号",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


查询设备的实时测点数据
Post
/openapi/getDeviceRealTimeData

根据设备的ps_key或SN查询实时测点数据。 注意： 1、该接口返回的数据的单位都是最小单位，如发电量数据对应单位是Wh，功率数据对应的单位是W，电流对应单位是A，电压对应单位是V。 2、数据刷新时间是5分钟左右，建议该接口调用频率不能低于5分钟。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
point_id_list
List
是
["83022","83033"]
测点id集合，具体开放测点定义信息通过常用遥测测点获取。
ps_key_list
List
否
["972018_11_0_0","971822_11_0_0"]
ps_key集合（需要传同一设备类型）
device_type
Integer
是
11
设备类型（可见附录1查询）
sn_list
List
否
['A21B1801347','A29B1902347']
sn集合，ps_key_list与sn_list只需传入一个
{
	"device_type":11,
	"point_id_list":[
		"83022",
		"83033"
	],
	"ps_key_list":[
		"972018_11_0_0",
		"971822_11_0_0",
		"972131_11_0_0",
		"972192_11_0_0",
		"972245_11_0_0",
		"971884_11_0_0",
		"971868_11_0_0",
		"972231_11_0_0",
		"971556_11_0_0",
		"971812_11_0_0",
		"971841_11_0_0",
		"972292_11_0_0",
		"971671_11_0_0",
		"972402_11_0_0",
		"972079_11_0_0",
		"972361_11_0_0",
		"971779_11_0_0",
		"971867_11_0_0",
		"972086_11_0_0",
		"972262_11_0_0",
		"971891_11_0_0",
		"972393_11_0_0",
		"972359_11_0_0",
		"972270_11_0_0",
		"972068_11_0_0",
		"972062_11_0_0",
		"972213_11_0_0",
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
2024112728b644398654b9c98150d2f2
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.device_point_list
List
--
每个设备测点值集合
result_data.device_point_list.device_point
Map
--
测点集合
result_data.device_point_list.device_point.communication_dev_sn
String
A235**07928
设备对应的通信设备的SN
result_data.device_point_list.device_point.dev_fault_status
Integer
4
设备故障告警状态 1：故障 2：告警 4：正常
result_data.device_point_list.device_point.dev_status
Integer
1
设备当前在线离线状态：0：离线，1：在线
result_data.device_point_list.device_point.device_name
String
Hybrid Inverter2
设备名称
result_data.device_point_list.device_point.device_sn
String
A23519**928
设备SN
result_data.device_point_list.device_point.device_time
String
20241127151500
设备数据更新时间
result_data.device_point_list.device_point.p+pointid
Map
--
测点对应值，如p1表示point_id=1的测点值
result_data.device_point_list.device_point.ps_id
Integer
970645
电站ID
result_data.device_point_list.device_point.ps_key
String
970645_11_0_0
设备的ps_key
result_data.device_point_list.device_point.uuid
Integer
10941275
设备UUID
result_data.fail_ps_key_list
List
["700926130_22_247_2","700926130_22_247_3"]
不合法的ps_key集合
2.1 成功示例
{
	"req_serial_num":"2024112728b644398654b9c98150d2f2",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"fail_ps_key_list":[],
		"device_point_list":[
			{
				"device_point":{
					"device_name":"贺伟26.4kWB2342458280的电站陈程程",
					"dev_fault_status":4,
					"ps_key":"970645_11_0_0",
					"device_sn":null,
					"dev_status":1,
					"ps_id":970645,
					"communication_dev_sn":null,
					"uuid":10941275,
					"p83022":"108500.0",
					"p83033":"9276.0",
					"device_time":"20241127151500"
				}
			},
			{
				"device_point":{
					"device_name":"黄拥军26.4kwB2342457345的电站",
					"dev_fault_status":4,
					"ps_key":"970956_11_0_0",
					"device_sn":null,
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
3. 更多信息
3.1 设备测点
设备类型	测点ID	测点名称	单位
逆变器	1	当日发电	Wh
87	当月发电	Wh
88	当年发电	Wh
2	总发电量	Wh
67	日理论发电量	Wh
24	总有功功率	W
25	总无功功率	var
14	总直流功率	W
43	总视在功率	VA
26	总功率因数	
18	A相电压	V
19	B相电压	V
20	C相电压	V
21	A相电流	A
22	B相电流	A
23	C相电流	A
94	方阵绝缘阻抗	kΩ
27	电网频率	Hz
7356	总运行时间	h
3	总并网运行时间	h
15	A-B线电压	V
16	B-C线电压	V
17	C-A线电压	V
95	母线电压	V
90	负极对地电压	V
120	AFCI故障次数	
4	机内空气温度	℃
33	模块1温度	℃
34	模块2温度	℃
35	模块3温度	℃
36	模块4温度	℃
37	模块5温度	℃
38	模块6温度	℃
39	正极对地阻抗值	Ω
40	负极对地阻抗值	Ω
41	限功率实际值	W
42	无功调节实际值	va
5	MPPT1电压	V
7	MPPT2电压	V
9	MPPT3电压	V
45	MPPT4电压	V
47	MPPT5电压	V
49	MPPT6电压	V
51	MPPT7电压	V
53	MPPT8电压	V
55	MPPT9电压	V
57	MPPT10电压	V
7401	MPPT11电压	V
7402	MPPT12电压	V
7723	MPPT13电压	V
7725	MPPT14电压	V
7727	MPPT15电压	V
7729	MPPT16电压	V
7731	MPPT17电压	V
7733	MPPT18电压	V
7735	MPPT19电压	V
7737	MPPT20电压	V
6	MPPT1电流	A
8	MPPT2电流	A
10	MPPT3电流	A
46	MPPT4电流	A
48	MPPT5电流	A
50	MPPT6电流	A
52	MPPT7电流	A
54	MPPT8电流	A
56	MPPT9电流	A
58	MPPT10电流	A
7451	MPPT11电流	A
7452	MPPT12电流	A
7724	MPPT13电流	A
7726	MPPT14电流	A
7728	MPPT15电流	A
7730	MPPT16电流	A
7732	MPPT17电流	A
7734	MPPT18电流	A
7736	MPPT19电流	A
7738	MPPT20电流	A
96	组串1电压	V
97	组串2电压	V
98	组串3电压	V
99	组串4电压	V
100	组串5电压	V
101	组串6电压	V
102	组串7电压	V
103	组串8电压	V
104	组串9电压	V
105	组串10电压	V
106	组串11电压	V
107	组串12电压	V
108	组串13电压	V
109	组串14电压	V
110	组串15电压	V
111	组串16电压	V
112	组串17电压	V
113	组串18电压	V
7166	组串19电压	V
7167	组串20电压	V
7168	组串21电压	V
7169	组串22电压	V
7170	组串23电压	V
7171	组串24电压	V
7172	组串25电压	V
7173	组串26电压	V
7174	组串27电压	V
7175	组串28电压	V
7176	组串29电压	V
7177	组串30电压	V
7178	组串31电压	V
7179	组串32电压	V
7707	组串33电压	V
7709	组串34电压	V
7711	组串35电压	V
7713	组串36电压	V
7715	组串37电压	V
7717	组串38电压	V
7719	组串39电压	V
7721	组串40电压	V
70	组串1电流	A
71	组串2电流	A
72	组串3电流	A
73	组串4电流	A
74	组串5电流	A
75	组串6电流	A
76	组串7电流	A
77	组串8电流	A
78	组串9电流	A
79	组串10电流	A
80	组串11电流	A
81	组串12电流	A
82	组串13电流	A
83	组串14电流	A
84	组串15电流	A
85	组串16电流	A
92	组串17电流	A
93	组串18电流	A
313	组串19电流	A
314	组串20电流	A
315	组串21电流	A
316	组串22电流	A
317	组串23电流	A
318	组串24电流	A
319	组串25电流	A
320	组串26电流	A
321	组串27电流	A
322	组串28电流	A
323	组串29电流	A
324	组串30电流	A
325	组串31电流	A
326	组串32电流	A
7708	组串33电流	A
7710	组串34电流	A
7712	组串35电流	A
7714	组串36电流	A
7716	组串37电流	A
7718	组串38电流	A
7720	组串39电流	A
7722	组串40电流	A
29	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网充电，6144-智能建站状态，20-微网运行	
汇流箱	1002	机内温度	℃
1001	直流母线电压	V
1006	总直流功率	W
1005	总直流电流	A
1009	第1路电流	A
1010	第2路电流	A
1011	第3路电流	A
1012	第4路电流	A
1013	第5路电流	A
1014	第6路电流	A
1015	第7路电流	A
1016	第8路电流	A
1017	第9路电流	A
1018	第10路电流	A
1019	第11路电流	A
1020	第12路电流	A
1021	第13路电流	A
1022	第14路电流	A
1023	第15路电流	A
1024	第16路电流	A
1025	第17路电流	A
1026	第18路电流	A
1027	第19路电流	A
1028	第20路电流	A
1029	第21路电流	A
1030	第22路电流	A
1031	第23路电流	A
1032	第24路电流	A
环境检测仪	2003	平面瞬时辐照	W/㎡
2001	平面日辐射量	Wh/㎡
2002	平面总辐射量	Wh/㎡
2007	斜面瞬时辐照	W/㎡
2005	斜面日辐射量	Wh/㎡
2006	斜面总辐射量	Wh/㎡
2009	环境温度	℃
2010	组件温度	℃
2016	风速	m/s
2011	风速等级	
2012	风向度数	°
2014	大气压力	hPa
2015	环境湿度	%RH
2022	雨量	mm
2026	降水量	mm
2100	温度1（背板温度）	℃
2101	温度2	℃
2102	温度3	℃
2103	温度4	℃
2104	温度5	℃
2105	露点	
2106	土湿1	
2107	土湿2	
2108	土湿3	
2109	CO₂	
2110	蒸发	
2111	总辐射1瞬时值	
2114	总辐射2瞬时值	
2112	散射辐射瞬时值	
2113	直接辐射瞬时值	
2115	净辐射瞬时值	
2116	光合辐射瞬时值	
2117	紫外辐射瞬时值	
2118	风向瞬时值	
2119	风速瞬时值	
2120	2分钟风速	
2121	10分钟风速	
2122	雨量时间间隔累计值	
2123	日照时间间隔累计值	
2124	总辐射1时间间隔累计值	
2127	总辐射2时间间隔累计值	
2125	散射辐射时间间隔累计值	
2126	直接辐射时间间隔累计值	
2128	净辐射时间间隔累计值	
2129	光合辐射时间间隔累计值	
2130	紫外辐射时间间隔累计值	
2131	雨量日累计	
2132	日照日累计	
2133	总辐射1日累计值	
2136	总辐射2日累计值	
2134	散射辐射日累计值	
2135	直接辐射日累计值	
2137	净辐射日累计值	
2138	光合辐射日累计值	
2139	紫外辐射日累计值	
电表	8030	正向有功电度	Wh
8031	反向有功电度	Wh
8062	日正向有功电度	Wh
8063	日反向有功电度	Wh
8032	正向无功电度	varh
8033	反向无功电度	varh
8034	峰正向有功电度	Wh
8035	峰反向有功电度	Wh
8038	谷正向有功电度	Wh
8039	谷反向有功电度	Wh
8042	平正向有功电度	Wh
8043	平反向有功电度	Wh
8058	尖正向有功电度	Wh
8059	尖反向有功电度	Wh
8036	峰正向无功电度	Wh
8037	峰反向无功电度	Wh
8040	谷正向无功电度	Wh
8041	谷反向无功电度	Wh
8044	平正向无功电度	Wh
8045	平反向无功电度	Wh
8060	尖正向无功电度	Wh
8061	尖反向无功电度	Wh
8000	A相电压	V
8001	B相电压	V
8002	C相电压	V
8003	A-B线电压	V
8004	B-C线电压	V
8005	C-A线电压	V
8006	A相电流	A
8007	B相电流	A
8008	C相电流	A
8064	频率	Hz
8018	电表有功功率	W
8022	无功功率	var
8014	功率因数	
8026	视在功率	VA
8076	电表A相有功功率	W
8077	电表B相有功功率	W
8078	电表C相有功功率	W
8084	日直接消耗电量	Wh
8085	总直接消耗电量	Wh
通信装置	10555	AI电压信号1	V
10557	AI电压信号2	V
10559	AI电压信号3	V
10561	AI电压信号4	V
10575	AI电流信号1	mA
10576	AI电流信号2	mA
10577	AI电流信号3	mA
10578	AI电流信号4	mA
10563	PT信号1	℃
10565	PT信号2	℃
10567	DO信号1	
10569	DO信号2	
10571	DO信号3	
10573	DO信号4	
10026	总功率	W
10046	总无功功率	var
10587	总有功功率	W
10510	移动网络信号强度	
10511	WLAN信号强度	
10028	总发电量	Wh
储能逆变器	13011	有功功率	W
13012	总无功功率	var
13003	总直流功率	W
13013	总功率因数	
13157	A相电压	V
13158	B相电压	V
13159	C相电压	V
13008	A相电流	A
13009	B相电流	A
13010	C相电流	A
13160	方阵绝缘阻抗	kΩ
13007	电网频率	Hz
18065	离网口A相功率	W
18066	离网口B相功率	W
18067	离网口C相功率	W
18068	离网口总功率	W
18062	离网口A相电流	A
18063	离网口B相电流	A
18064	离网口C相电流	A
13020	总运行时间	H
13112	日PV发电量	Wh
13134	总PV发电量	Wh
13187	交流电压	V
13188	交流电流	A
13004	A-B线电压	V
13005	B-C线电压	V
13006	C-A线电压	V
13019	机内空气温度	℃
13161	母线电压	V
13001	MPPT1电压	V
13105	MPPT2电压	V
13107	MPPT3电压	V
13109	MPPT4电压	V
13002	MPPT1电流	A
13106	MPPT2电流	A
13108	MPPT3电流	A
13110	MPPT4电流	A
13122	今日馈网	Wh
13125	累计馈网	Wh
13147	今日取电	Wh
13148	累计取电	Wh
13149	电网取电功率	W
13121	馈网功率	W
13173	今日PV馈网	Wh
13175	累计PV馈网	Wh
13141	电池电量	
13029	今日电池放电	Wh
13028	今日电池充电	Wh
13138	电池电压	V
13139	电池电流	A
13035	累计电池放电	Wh
13034	累计电池充电	Wh
13142	电池健康度	
13143	电池温度	℃
13162	最大充电电流(BMS)	A
13163	最大放电电流(BMS)	A
13174	今日PV电池充电	Wh
13176	累计PV电池充电	Wh
13126	电池充电功率	W
13150	电池放电功率	W
13199	日负载用电	Wh
13137	总直接消耗电量	Wh
13119	负载功率	W
13130	总负载用电	Wh
13116	日直接消耗电量	Wh
13144	日自发自用率	
13016	总充电时间	H
13017	总放电时间	H
13018	总视在功率	VA
13023	日充电时间	H
13024	日放电时间	H
13118	年直接消耗电量	Wh
13165	MDSP离网启机状态	
13166	SDSP工作模式	
13167	SDSP离网启机状态	
13168	DI状态	
13169	电池电压（BMS）	V
13170	电池SOC（BMS）	
13171	EMS状态	
13172	日自给自足率	
13140	电池容量(kWh)	Wh
18075	通道二总视在功率	VA
18076	通道二A相视在功率	VA
18077	通道二B相视在功率	VA
18078	通道二C相视在功率	VA
18079	通道二总有功功率	W
18080	通道二A相有功功率	W
18081	通道二B相有功功率	W
18082	通道二C相有功功率	W
18083	通道二总无功功率	var
18084	通道二A相无功功率	var
18085	通道二B相无功功率	var
18086	通道二C相无功功率	var
18087	通道二功率因数	
18088	通道二总取电电量	Wh
18089	通道二A相取电电量	Wh
18090	通道二B相取电电量	Wh
18091	通道二C相取电电量	Wh
18092	通道二总馈网电量	Wh
18093	通道二A相馈网电量	Wh
18094	通道二B相馈网电量	Wh
18095	通道二C相馈网电量	Wh
18103	离网口A相电压	V
18104	离网口B相电压	V
18105	离网口C相电压	V
18108	电表A相电压	V
18109	电表B相电压	V
18110	电表C相电压	V
13146	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网直流充电，20-微网运行	
通讯模块	23001	无线信号强度	
23014	WLAN信号强度	
23008	卡号	
电池	58601	电池电压	V
58602	电池电流	A
58603	电池温度	℃
58604	电池剩余电量	
58605	电池健康度	
58606	累计电池充电	Wh
58607	累计电池放电	Wh
58608	电池运行状态（0:空闲,1:待机,2:运行,3:故障,4:关机,5:升级,6:校正,7:测试）	
58609	标准健康状态	
58610	电芯电压最大值	mV
58611	电芯电压最大值位置	
58612	电芯电压最小值	mV
58613	电芯电压最小值位置	
58614	模组温度最高值	℃
58615	模组温度最高值位置	
58616	模组温度最低值	℃
58617	模组温度最低值位置	
58618	模组1电芯电压最大值	mV
58619	模组2电芯电压最大值	mV
58620	模组3电芯电压最大值	mV
58621	模组4电芯电压最大值	mV
58622	模组5电芯电压最大值	mV
58623	模组6电芯电压最大值	mV
58624	模组7电芯电压最大值	mV
58625	模组8电芯电压最大值	mV
58626	模组1电芯电压最小值	mV
58627	模组2电芯电压最小值	mV
58628	模组3电芯电压最小值	mV
58629	模组4电芯电压最小值	mV
58630	模组5电芯电压最小值	mV
58631	模组6电芯电压最小值	mV
58632	模组7电芯电压最小值	mV
58633	模组8电芯电压最小值	mV
58635	直流接触器状态	
58636	故障模组位置	
EMS	24620	储能日充电量	Wh
24622	储能总充电量	Wh
24621	储能日放电量	Wh
24623	储能总放电量	Wh
24624	光伏有功功率	W
24625	储能有功功率	W
24626	电网有功功率	W
24627	光伏日发电量	Wh
24628	光伏总发电量	Wh
24629	储能SOC	%
24630	储能剩余电量	Wh
24631	有功负载	W
LC	59502	软件版本	
59546	日充电量	Wh
59535	总充电量	Wh
59547	日放电量	Wh
59536	总放电量	Wh
59541	总有功功率	W
59542	总无功功率	var
59551	工作模式	
59552	系统工作状态（0:初始状态,1:自检,2:自检失败,3:启动中,4:运行,5:告警运行,6:待机,7:停机中,8:停机,9:紧急停机,10:故障停机）	
59705	设备S/N	
PCS	44010	整机总有功功率	W
44011	整机总无功功率	var
44012	整机功率因数	
44029	整机电网频率	Hz
44025	工作模式	
44231	运行状态（0:并网运行,4096:离网运行,4608:初始待机,5632:启动中,37120:告警运行,33024:降额运行,5120:热待机,4864:按键关机,21760:故障停机,5376:紧急停机,12288:零功率状态运行,4610:运行）	
44244	机内空气温度	℃
44803	设备S/N	
44823	PCS-DSP版本号	
44824	PCS-CPLD版本号	
CMU	59002	总电压	
59003	总电流	
59004	SOC	
59006	电池总容量	
59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59403	软件版本	
BSC	59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59064	最高电芯电压位置(#BMU~#Cell)	
59065	最低电芯电压位置(#BMU~#Cell)	
59066	最高电芯温度位置(#BMU~#Cell)	
59067	最低电芯温度位置(#BMU~#Cell)	
充电桩	33708	充电功率	kW
33722	最小充电功率	kW
33723	最大充电功率	kW
33702	A相充电电压	V
33704	B相充电电压	V
33706	C相充电电压	V
33710	CP电压	V
33707	C相充电电流	A
33705	B相充电电流	A
33703	A相充电电流	A
33728	最大充电电流	A
33729	最小充电电流	A
33716	充电状态（空闲(未插枪):1-- 待机(已插枪):2--充电中:3--充电暂停(桩端):4--充电暂停(车端):5--充电完成:6--预约:7--禁用:8--故障:9）	
微逆






51301	运行状态（21760:故障停机,0:并网运行,1024:维护模式运行,2048:强制模式运行,4096:离网运行,8192:开环,4608:初始待机,32768:停机,5120:待机,5632:启动中,33024:降额运行,33280:调度运行,4369:初始状态,4864:按键关机,37120:告警运行）	
51346	当日发电	Wh
51302	总发电量	Wh
51303	总有功功率	W
51304	总无功功率	var
51305	总直流功率	W
51306	总视在功率	VA
51307	总功率因数	
51308	电网频率	Hz
51309	交流电压	V
51312	交流电流	A
51315	PV1电压	V
51317	PV2电压	V
51319	PV3电压	V
51321	PV4电压	V
51323	PV5电压	V
51325	PV6电压	V
51316	PV1电流	A
51318	PV2电流	A
51320	PV3电流	A
51322	PV4电流	A
51324	PV5电流	A
51326	PV6电流	A
51333	PV1功率	W
51334	PV2功率	W
51335	PV3功率	W
51336	PV4功率	W
51337	PV5功率	W
51338	PV6功率	W
51347	PV1当日发电	Wh
51348	PV2当日发电	Wh
51349	PV3当日发电	Wh
51350	PV4当日发电	Wh
51351	PV5当日发电	Wh
51352	PV6当日发电	Wh
51339	PV1累计发电	Wh
51340	PV2累计发电	Wh
51341	PV3累计发电	Wh
51342	PV4累计发电	Wh
51343	PV5累计发电	Wh
51344	PV6累计发电	Wh







查询同类型设备的历史测点分钟级数据
Post
/openapi/getDevicePointMinuteDataList

根据多个相同类型设备ps_key和测点ID、指定时间区间（电站所在时区），查询设备测点对应的分钟数据，查询的时间区间最大为3小时，设备数量最多50个。如果当前查询的设备的某个测点没有数据，那么接口不会返回这个测点。单次请求测点的数量必须小于50个。历史数据接口不返回当天的数据。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
end_time_stamp
String
是
20211122080000
结束时间 （电站所在时区时间），格式为：yyyyMMddHHmmss
minute_interval
String
否
15
分钟的时间间隔 如：15 代表每15分钟的测点数据 如果不传或者为空，则默认查询每5分钟的测点数据，必须为5的整数倍
points
String
是
p83024
p+测点ID，如p3022,p3024，多个测点使用英文逗号隔开，具体开放测点定义信息通过常用遥测测点获取。
ps_key_list
List
是
["184741_1_1_1"]
设备ps_key集合（相同类型的设备）
start_time_stamp
String
是
20240724110000
开始时间 (电站所在时区时间) ，格式为：yyyyMMddHHmmss
is_get_data_acquisition_time
String
否
1
如果有值且为1，则返回数据采集时间
is_get_point_dict
String
否
1
是否需要返回测点字典，1：需要，0：不需要，不传默认为不需要
{
	"start_time_stamp":"20211122080000",
	"points":"p5,p6,p7,p8,p9,p10,p18,p19,p20,p21,p22,p23,p24,p45,p46,p47,p48,p49,p50,p51,p52,p53,p54",
	"end_time_stamp":"20211122105000",
	"minute_interval":10,
	"ps_key_list":[
		"184741_1_1_1"
	],
	"is_get_data_acquisition_time": "1"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202411275316448b87dbc526d8a5efc4
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data.{ps_key}.{p+pointid}
String
p23
测点值（说明：该出参如：p1,p83022）
result_data
Map
--
返回数据
result_data.{ps_key}
List
["700926130_22_247_2","700926130_22_247_3"]
设备的ps_key
result_data.{ps_key}.time_stamp
String
20211122080000
时间（电站所在时区时间）
result_data.{ps_key}.pST001
String
20211122105000
数据上传时间
2.1 成功示例
{
	"req_serial_num":"202411275316448b87dbc526d8a5efc4",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"184741_1_1_1":[
			{
				"p23":"1.1",
				"p22":"1.0",
				"p24":"626.0",
				"time_stamp":"20211122080000",
				"p5":"474.6",
				"p6":"0.5",
				"p18":"230.6",
				"p7":"673.3",
				"p8":"0.5",
				"p19":"229.3",
				"p21":"1.2",
				"p20":"229.3"
			},
			{
				"p23":"1.2",
				"p22":"1.2",
				"p24":"708.0",
				"time_stamp":"20211122081000",
				"p5":"492.8",
				"p6":"0.6",
				"p18":"230.4",
				"p7":"680.9",
				"p8":"0.6",
				"p19":"229.4",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
3. 更多信息
3.1 设备测点
设备类型	测点ID	测点名称	单位
逆变器	1	当日发电	Wh
87	当月发电	Wh
88	当年发电	Wh
2	总发电量	Wh
67	日理论发电量	Wh
24	总有功功率	W
25	总无功功率	var
14	总直流功率	W
43	总视在功率	VA
26	总功率因数	
18	A相电压	V
19	B相电压	V
20	C相电压	V
21	A相电流	A
22	B相电流	A
23	C相电流	A
94	方阵绝缘阻抗	kΩ
27	电网频率	Hz
7356	总运行时间	h
3	总并网运行时间	h
15	A-B线电压	V
16	B-C线电压	V
17	C-A线电压	V
95	母线电压	V
90	负极对地电压	V
120	AFCI故障次数	
4	机内空气温度	℃
33	模块1温度	℃
34	模块2温度	℃
35	模块3温度	℃
36	模块4温度	℃
37	模块5温度	℃
38	模块6温度	℃
39	正极对地阻抗值	Ω
40	负极对地阻抗值	Ω
41	限功率实际值	W
42	无功调节实际值	va
5	MPPT1电压	V
7	MPPT2电压	V
9	MPPT3电压	V
45	MPPT4电压	V
47	MPPT5电压	V
49	MPPT6电压	V
51	MPPT7电压	V
53	MPPT8电压	V
55	MPPT9电压	V
57	MPPT10电压	V
7401	MPPT11电压	V
7402	MPPT12电压	V
7723	MPPT13电压	V
7725	MPPT14电压	V
7727	MPPT15电压	V
7729	MPPT16电压	V
7731	MPPT17电压	V
7733	MPPT18电压	V
7735	MPPT19电压	V
7737	MPPT20电压	V
6	MPPT1电流	A
8	MPPT2电流	A
10	MPPT3电流	A
46	MPPT4电流	A
48	MPPT5电流	A
50	MPPT6电流	A
52	MPPT7电流	A
54	MPPT8电流	A
56	MPPT9电流	A
58	MPPT10电流	A
7451	MPPT11电流	A
7452	MPPT12电流	A
7724	MPPT13电流	A
7726	MPPT14电流	A
7728	MPPT15电流	A
7730	MPPT16电流	A
7732	MPPT17电流	A
7734	MPPT18电流	A
7736	MPPT19电流	A
7738	MPPT20电流	A
96	组串1电压	V
97	组串2电压	V
98	组串3电压	V
99	组串4电压	V
100	组串5电压	V
101	组串6电压	V
102	组串7电压	V
103	组串8电压	V
104	组串9电压	V
105	组串10电压	V
106	组串11电压	V
107	组串12电压	V
108	组串13电压	V
109	组串14电压	V
110	组串15电压	V
111	组串16电压	V
112	组串17电压	V
113	组串18电压	V
7166	组串19电压	V
7167	组串20电压	V
7168	组串21电压	V
7169	组串22电压	V
7170	组串23电压	V
7171	组串24电压	V
7172	组串25电压	V
7173	组串26电压	V
7174	组串27电压	V
7175	组串28电压	V
7176	组串29电压	V
7177	组串30电压	V
7178	组串31电压	V
7179	组串32电压	V
7707	组串33电压	V
7709	组串34电压	V
7711	组串35电压	V
7713	组串36电压	V
7715	组串37电压	V
7717	组串38电压	V
7719	组串39电压	V
7721	组串40电压	V
70	组串1电流	A
71	组串2电流	A
72	组串3电流	A
73	组串4电流	A
74	组串5电流	A
75	组串6电流	A
76	组串7电流	A
77	组串8电流	A
78	组串9电流	A
79	组串10电流	A
80	组串11电流	A
81	组串12电流	A
82	组串13电流	A
83	组串14电流	A
84	组串15电流	A
85	组串16电流	A
92	组串17电流	A
93	组串18电流	A
313	组串19电流	A
314	组串20电流	A
315	组串21电流	A
316	组串22电流	A
317	组串23电流	A
318	组串24电流	A
319	组串25电流	A
320	组串26电流	A
321	组串27电流	A
322	组串28电流	A
323	组串29电流	A
324	组串30电流	A
325	组串31电流	A
326	组串32电流	A
7708	组串33电流	A
7710	组串34电流	A
7712	组串35电流	A
7714	组串36电流	A
7716	组串37电流	A
7718	组串38电流	A
7720	组串39电流	A
7722	组串40电流	A
29	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网充电，6144-智能建站状态，20-微网运行	
汇流箱	1002	机内温度	℃
1001	直流母线电压	V
1006	总直流功率	W
1005	总直流电流	A
1009	第1路电流	A
1010	第2路电流	A
1011	第3路电流	A
1012	第4路电流	A
1013	第5路电流	A
1014	第6路电流	A
1015	第7路电流	A
1016	第8路电流	A
1017	第9路电流	A
1018	第10路电流	A
1019	第11路电流	A
1020	第12路电流	A
1021	第13路电流	A
1022	第14路电流	A
1023	第15路电流	A
1024	第16路电流	A
1025	第17路电流	A
1026	第18路电流	A
1027	第19路电流	A
1028	第20路电流	A
1029	第21路电流	A
1030	第22路电流	A
1031	第23路电流	A
1032	第24路电流	A
环境检测仪	2003	平面瞬时辐照	W/㎡
2001	平面日辐射量	Wh/㎡
2002	平面总辐射量	Wh/㎡
2007	斜面瞬时辐照	W/㎡
2005	斜面日辐射量	Wh/㎡
2006	斜面总辐射量	Wh/㎡
2009	环境温度	℃
2010	组件温度	℃
2016	风速	m/s
2011	风速等级	
2012	风向度数	°
2014	大气压力	hPa
2015	环境湿度	%RH
2022	雨量	mm
2026	降水量	mm
2100	温度1（背板温度）	℃
2101	温度2	℃
2102	温度3	℃
2103	温度4	℃
2104	温度5	℃
2105	露点	
2106	土湿1	
2107	土湿2	
2108	土湿3	
2109	CO₂	
2110	蒸发	
2111	总辐射1瞬时值	
2114	总辐射2瞬时值	
2112	散射辐射瞬时值	
2113	直接辐射瞬时值	
2115	净辐射瞬时值	
2116	光合辐射瞬时值	
2117	紫外辐射瞬时值	
2118	风向瞬时值	
2119	风速瞬时值	
2120	2分钟风速	
2121	10分钟风速	
2122	雨量时间间隔累计值	
2123	日照时间间隔累计值	
2124	总辐射1时间间隔累计值	
2127	总辐射2时间间隔累计值	
2125	散射辐射时间间隔累计值	
2126	直接辐射时间间隔累计值	
2128	净辐射时间间隔累计值	
2129	光合辐射时间间隔累计值	
2130	紫外辐射时间间隔累计值	
2131	雨量日累计	
2132	日照日累计	
2133	总辐射1日累计值	
2136	总辐射2日累计值	
2134	散射辐射日累计值	
2135	直接辐射日累计值	
2137	净辐射日累计值	
2138	光合辐射日累计值	
2139	紫外辐射日累计值	
电表	8030	正向有功电度	Wh
8031	反向有功电度	Wh
8062	日正向有功电度	Wh
8063	日反向有功电度	Wh
8032	正向无功电度	varh
8033	反向无功电度	varh
8034	峰正向有功电度	Wh
8035	峰反向有功电度	Wh
8038	谷正向有功电度	Wh
8039	谷反向有功电度	Wh
8042	平正向有功电度	Wh
8043	平反向有功电度	Wh
8058	尖正向有功电度	Wh
8059	尖反向有功电度	Wh
8036	峰正向无功电度	Wh
8037	峰反向无功电度	Wh
8040	谷正向无功电度	Wh
8041	谷反向无功电度	Wh
8044	平正向无功电度	Wh
8045	平反向无功电度	Wh
8060	尖正向无功电度	Wh
8061	尖反向无功电度	Wh
8000	A相电压	V
8001	B相电压	V
8002	C相电压	V
8003	A-B线电压	V
8004	B-C线电压	V
8005	C-A线电压	V
8006	A相电流	A
8007	B相电流	A
8008	C相电流	A
8064	频率	Hz
8018	电表有功功率	W
8022	无功功率	var
8014	功率因数	
8026	视在功率	VA
8076	电表A相有功功率	W
8077	电表B相有功功率	W
8078	电表C相有功功率	W
8084	日直接消耗电量	Wh
8085	总直接消耗电量	Wh
通信装置	10555	AI电压信号1	V
10557	AI电压信号2	V
10559	AI电压信号3	V
10561	AI电压信号4	V
10575	AI电流信号1	mA
10576	AI电流信号2	mA
10577	AI电流信号3	mA
10578	AI电流信号4	mA
10563	PT信号1	℃
10565	PT信号2	℃
10567	DO信号1	
10569	DO信号2	
10571	DO信号3	
10573	DO信号4	
10026	总功率	W
10046	总无功功率	var
10587	总有功功率	W
10510	移动网络信号强度	
10511	WLAN信号强度	
10028	总发电量	Wh
储能逆变器	13011	有功功率	W
13012	总无功功率	var
13003	总直流功率	W
13013	总功率因数	
13157	A相电压	V
13158	B相电压	V
13159	C相电压	V
13008	A相电流	A
13009	B相电流	A
13010	C相电流	A
13160	方阵绝缘阻抗	kΩ
13007	电网频率	Hz
18065	离网口A相功率	W
18066	离网口B相功率	W
18067	离网口C相功率	W
18068	离网口总功率	W
18062	离网口A相电流	A
18063	离网口B相电流	A
18064	离网口C相电流	A
13020	总运行时间	H
13112	日PV发电量	Wh
13134	总PV发电量	Wh
13187	交流电压	V
13188	交流电流	A
13004	A-B线电压	V
13005	B-C线电压	V
13006	C-A线电压	V
13019	机内空气温度	℃
13161	母线电压	V
13001	MPPT1电压	V
13105	MPPT2电压	V
13107	MPPT3电压	V
13109	MPPT4电压	V
13002	MPPT1电流	A
13106	MPPT2电流	A
13108	MPPT3电流	A
13110	MPPT4电流	A
13122	今日馈网	Wh
13125	累计馈网	Wh
13147	今日取电	Wh
13148	累计取电	Wh
13149	电网取电功率	W
13121	馈网功率	W
13173	今日PV馈网	Wh
13175	累计PV馈网	Wh
13141	电池电量	
13029	今日电池放电	Wh
13028	今日电池充电	Wh
13138	电池电压	V
13139	电池电流	A
13035	累计电池放电	Wh
13034	累计电池充电	Wh
13142	电池健康度	
13143	电池温度	℃
13162	最大充电电流(BMS)	A
13163	最大放电电流(BMS)	A
13174	今日PV电池充电	Wh
13176	累计PV电池充电	Wh
13126	电池充电功率	W
13150	电池放电功率	W
13199	日负载用电	Wh
13137	总直接消耗电量	Wh
13119	负载功率	W
13130	总负载用电	Wh
13116	日直接消耗电量	Wh
13144	日自发自用率	
13016	总充电时间	H
13017	总放电时间	H
13018	总视在功率	VA
13023	日充电时间	H
13024	日放电时间	H
13118	年直接消耗电量	Wh
13165	MDSP离网启机状态	
13166	SDSP工作模式	
13167	SDSP离网启机状态	
13168	DI状态	
13169	电池电压（BMS）	V
13170	电池SOC（BMS）	
13171	EMS状态	
13172	日自给自足率	
13140	电池容量(kWh)	Wh
18075	通道二总视在功率	VA
18076	通道二A相视在功率	VA
18077	通道二B相视在功率	VA
18078	通道二C相视在功率	VA
18079	通道二总有功功率	W
18080	通道二A相有功功率	W
18081	通道二B相有功功率	W
18082	通道二C相有功功率	W
18083	通道二总无功功率	var
18084	通道二A相无功功率	var
18085	通道二B相无功功率	var
18086	通道二C相无功功率	var
18087	通道二功率因数	
18088	通道二总取电电量	Wh
18089	通道二A相取电电量	Wh
18090	通道二B相取电电量	Wh
18091	通道二C相取电电量	Wh
18092	通道二总馈网电量	Wh
18093	通道二A相馈网电量	Wh
18094	通道二B相馈网电量	Wh
18095	通道二C相馈网电量	Wh
18103	离网口A相电压	V
18104	离网口B相电压	V
18105	离网口C相电压	V
18108	电表A相电压	V
18109	电表B相电压	V
18110	电表C相电压	V
13146	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网直流充电，20-微网运行	
通讯模块	23001	无线信号强度	
23014	WLAN信号强度	
23008	卡号	
电池	58601	电池电压	V
58602	电池电流	A
58603	电池温度	℃
58604	电池剩余电量	
58605	电池健康度	
58606	累计电池充电	Wh
58607	累计电池放电	Wh
58608	电池运行状态（0:空闲,1:待机,2:运行,3:故障,4:关机,5:升级,6:校正,7:测试）	
58609	标准健康状态	
58610	电芯电压最大值	mV
58611	电芯电压最大值位置	
58612	电芯电压最小值	mV
58613	电芯电压最小值位置	
58614	模组温度最高值	℃
58615	模组温度最高值位置	
58616	模组温度最低值	℃
58617	模组温度最低值位置	
58618	模组1电芯电压最大值	mV
58619	模组2电芯电压最大值	mV
58620	模组3电芯电压最大值	mV
58621	模组4电芯电压最大值	mV
58622	模组5电芯电压最大值	mV
58623	模组6电芯电压最大值	mV
58624	模组7电芯电压最大值	mV
58625	模组8电芯电压最大值	mV
58626	模组1电芯电压最小值	mV
58627	模组2电芯电压最小值	mV
58628	模组3电芯电压最小值	mV
58629	模组4电芯电压最小值	mV
58630	模组5电芯电压最小值	mV
58631	模组6电芯电压最小值	mV
58632	模组7电芯电压最小值	mV
58633	模组8电芯电压最小值	mV
58635	直流接触器状态	
58636	故障模组位置	
EMS	24620	储能日充电量	Wh
24622	储能总充电量	Wh
24621	储能日放电量	Wh
24623	储能总放电量	Wh
24624	光伏有功功率	W
24625	储能有功功率	W
24626	电网有功功率	W
24627	光伏日发电量	Wh
24628	光伏总发电量	Wh
24629	储能SOC	%
24630	储能剩余电量	Wh
24631	有功负载	W
LC	59502	软件版本	
59546	日充电量	Wh
59535	总充电量	Wh
59547	日放电量	Wh
59536	总放电量	Wh
59541	总有功功率	W
59542	总无功功率	var
59551	工作模式	
59552	系统工作状态（0:初始状态,1:自检,2:自检失败,3:启动中,4:运行,5:告警运行,6:待机,7:停机中,8:停机,9:紧急停机,10:故障停机）	
59705	设备S/N	
PCS	44010	整机总有功功率	W
44011	整机总无功功率	var
44012	整机功率因数	
44029	整机电网频率	Hz
44025	工作模式	
44231	运行状态（0:并网运行,4096:离网运行,4608:初始待机,5632:启动中,37120:告警运行,33024:降额运行,5120:热待机,4864:按键关机,21760:故障停机,5376:紧急停机,12288:零功率状态运行,4610:运行）	
44244	机内空气温度	℃
44803	设备S/N	
44823	PCS-DSP版本号	
44824	PCS-CPLD版本号	
CMU	59002	总电压	
59003	总电流	
59004	SOC	
59006	电池总容量	
59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59403	软件版本	
BSC	59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59064	最高电芯电压位置(#BMU~#Cell)	
59065	最低电芯电压位置(#BMU~#Cell)	
59066	最高电芯温度位置(#BMU~#Cell)	
59067	最低电芯温度位置(#BMU~#Cell)	
充电桩	33708	充电功率	kW
33722	最小充电功率	kW
33723	最大充电功率	kW
33702	A相充电电压	V
33704	B相充电电压	V
33706	C相充电电压	V
33710	CP电压	V
33707	C相充电电流	A
33705	B相充电电流	A
33703	A相充电电流	A
33728	最大充电电流	A
33729	最小充电电流	A
33716	充电状态（空闲(未插枪):1-- 待机(已插枪):2--充电中:3--充电暂停(桩端):4--充电暂停(车端):5--充电完成:6--预约:7--禁用:8--故障:9）	
微逆






51301	运行状态（21760:故障停机,0:并网运行,1024:维护模式运行,2048:强制模式运行,4096:离网运行,8192:开环,4608:初始待机,32768:停机,5120:待机,5632:启动中,33024:降额运行,33280:调度运行,4369:初始状态,4864:按键关机,37120:告警运行）	
51346	当日发电	Wh
51302	总发电量	Wh
51303	总有功功率	W
51304	总无功功率	var
51305	总直流功率	W
51306	总视在功率	VA
51307	总功率因数	
51308	电网频率	Hz
51309	交流电压	V
51312	交流电流	A
51315	PV1电压	V
51317	PV2电压	V
51319	PV3电压	V
51321	PV4电压	V
51323	PV5电压	V
51325	PV6电压	V
51316	PV1电流	A
51318	PV2电流	A
51320	PV3电流	A
51322	PV4电流	A
51324	PV5电流	A
51326	PV6电流	A
51333	PV1功率	W
51334	PV2功率	W
51335	PV3功率	W
51336	PV4功率	W
51337	PV5功率	W
51338	PV6功率	W
51347	PV1当日发电	Wh
51348	PV2当日发电	Wh
51349	PV3当日发电	Wh
51350	PV4当日发电	Wh
51351	PV5当日发电	Wh
51352	PV6当日发电	Wh
51339	PV1累计发电	Wh
51340	PV2累计发电	Wh
51341	PV3累计发电	Wh
51342	PV4累计发电	Wh
51343	PV5累计发电	Wh
51344	PV6累计发电	Wh
查询同类型设备的历史测点日月年数据
Post
/openapi/getDevicePointsDayMonthYearDataList

根据开始时间和结束时间以及多个相同类型设备的ps_key，和数据类型来获取设备的日、月、年测点数据，支持多测点查询，最多支持批量查询50个设备。 注意：该接口返回的数据的单位都是最小单位，如发电量数据对应的单位都是最小单位Wh，功率数据对应的单位都是最小单位W。日数据查询时间跨度最多100天，月数据查询时间跨度最多24个月，年数据查询时间跨度最多5年。历史数据接口不返回当天的数据。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
data_point
String
是
p13134,p13112,p13176,p13175
格式p+测点，多个测点使用逗号隔开。例如：如果查询的设备的ps_key是逆变器设备，则 p1表示逆变器发电量（返回数值对应单位为Wh），p2表示逆变器累计发电量（返回数值对应单位为Wh），p24表示逆变器总有功功率（返回数值对应单位为W），具体开放测点定义信息通过常用遥测测点获取。
data_type
String
是
2
1：均值，2：峰值，3：谷值，4：合计值（日维度的数据无合计值，月年维度的数据才有合计值） 多个使用逗号隔开。 如果是可以进行合计的数据，则： 查询日数据的时候，data_type为2， 查询月数据的时候，data_type为4， 查询年数据的时候，data_type为4
end_time
String
是
20240825
结束时间 说明： query_type为day的时候，日期格式为yyyyMMdd, query_type为month的时候，日期格式为yyyyMM, query_type为year的时候，日期格式为yyyy
order
Integer
是
0
排序方式： 1 倒序， 0 正序（按照时间的顺序）
ps_key_list
List
是
["700009960_14_1_1","700009960_14_3_1"]
设备ps_key集合（相同类型的设备）
query_type
String
是
1
查询类型： 查询日数据：1 查询月数据：2 查询年数据：3
start_time
String
是
20240823
开始时间 说明： query_type为day的时候，日期格式为yyyyMMdd, query_type为month的时候，日期格式为yyyyMM, query_type为year的时候，日期格式为yyyy
{
	"data_point":"p1",
	"end_time":"202411",
	"query_type":"2",
	"start_time":"202411",
	"ps_key_list":[
		"1598299_1_1_1"
	],
	"data_type":"4",
	"order":"0"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240827a1a74aecbdc4fe12f65055a6
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
1
返回数据
result_data.{ps_key}
Map
700009960_14_1_1
设备的ps_key
result_data.{ps_key}.{p+point_id}
List
[{"2": "371600.0000","time_stamp": "20240823"}
测点对应的数据集合
result_data.{ps_key}.{p+point_id}.{data_type}
String
371600.0000
对应的查询的data_type的数据（如：1），参照入参中的data_type参数
result_data.{ps_key}.{p+point_id}.time_stamp
String
20240823
对应的日期
2.1 成功示例
{
	"req_serial_num":"20241127184842d0bcff7b738d26b55c",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"1598299_1_1_1":{
			"p1":[
				{
					"4":"3708100.0000",
					"time_stamp":"202411"
				}
			]
		}
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
3. 更多信息
3.1 设备测点
设备类型	测点ID	测点名称	单位
逆变器	1	当日发电	Wh
87	当月发电	Wh
88	当年发电	Wh
2	总发电量	Wh
67	日理论发电量	Wh
24	总有功功率	W
25	总无功功率	var
14	总直流功率	W
43	总视在功率	VA
26	总功率因数	
18	A相电压	V
19	B相电压	V
20	C相电压	V
21	A相电流	A
22	B相电流	A
23	C相电流	A
94	方阵绝缘阻抗	kΩ
27	电网频率	Hz
7356	总运行时间	h
3	总并网运行时间	h
15	A-B线电压	V
16	B-C线电压	V
17	C-A线电压	V
95	母线电压	V
90	负极对地电压	V
120	AFCI故障次数	
4	机内空气温度	℃
33	模块1温度	℃
34	模块2温度	℃
35	模块3温度	℃
36	模块4温度	℃
37	模块5温度	℃
38	模块6温度	℃
39	正极对地阻抗值	Ω
40	负极对地阻抗值	Ω
41	限功率实际值	W
42	无功调节实际值	va
5	MPPT1电压	V
7	MPPT2电压	V
9	MPPT3电压	V
45	MPPT4电压	V
47	MPPT5电压	V
49	MPPT6电压	V
51	MPPT7电压	V
53	MPPT8电压	V
55	MPPT9电压	V
57	MPPT10电压	V
7401	MPPT11电压	V
7402	MPPT12电压	V
7723	MPPT13电压	V
7725	MPPT14电压	V
7727	MPPT15电压	V
7729	MPPT16电压	V
7731	MPPT17电压	V
7733	MPPT18电压	V
7735	MPPT19电压	V
7737	MPPT20电压	V
6	MPPT1电流	A
8	MPPT2电流	A
10	MPPT3电流	A
46	MPPT4电流	A
48	MPPT5电流	A
50	MPPT6电流	A
52	MPPT7电流	A
54	MPPT8电流	A
56	MPPT9电流	A
58	MPPT10电流	A
7451	MPPT11电流	A
7452	MPPT12电流	A
7724	MPPT13电流	A
7726	MPPT14电流	A
7728	MPPT15电流	A
7730	MPPT16电流	A
7732	MPPT17电流	A
7734	MPPT18电流	A
7736	MPPT19电流	A
7738	MPPT20电流	A
96	组串1电压	V
97	组串2电压	V
98	组串3电压	V
99	组串4电压	V
100	组串5电压	V
101	组串6电压	V
102	组串7电压	V
103	组串8电压	V
104	组串9电压	V
105	组串10电压	V
106	组串11电压	V
107	组串12电压	V
108	组串13电压	V
109	组串14电压	V
110	组串15电压	V
111	组串16电压	V
112	组串17电压	V
113	组串18电压	V
7166	组串19电压	V
7167	组串20电压	V
7168	组串21电压	V
7169	组串22电压	V
7170	组串23电压	V
7171	组串24电压	V
7172	组串25电压	V
7173	组串26电压	V
7174	组串27电压	V
7175	组串28电压	V
7176	组串29电压	V
7177	组串30电压	V
7178	组串31电压	V
7179	组串32电压	V
7707	组串33电压	V
7709	组串34电压	V
7711	组串35电压	V
7713	组串36电压	V
7715	组串37电压	V
7717	组串38电压	V
7719	组串39电压	V
7721	组串40电压	V
70	组串1电流	A
71	组串2电流	A
72	组串3电流	A
73	组串4电流	A
74	组串5电流	A
75	组串6电流	A
76	组串7电流	A
77	组串8电流	A
78	组串9电流	A
79	组串10电流	A
80	组串11电流	A
81	组串12电流	A
82	组串13电流	A
83	组串14电流	A
84	组串15电流	A
85	组串16电流	A
92	组串17电流	A
93	组串18电流	A
313	组串19电流	A
314	组串20电流	A
315	组串21电流	A
316	组串22电流	A
317	组串23电流	A
318	组串24电流	A
319	组串25电流	A
320	组串26电流	A
321	组串27电流	A
322	组串28电流	A
323	组串29电流	A
324	组串30电流	A
325	组串31电流	A
326	组串32电流	A
7708	组串33电流	A
7710	组串34电流	A
7712	组串35电流	A
7714	组串36电流	A
7716	组串37电流	A
7718	组串38电流	A
7720	组串39电流	A
7722	组串40电流	A
29	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网充电，6144-智能建站状态，20-微网运行	
汇流箱	1002	机内温度	℃
1001	直流母线电压	V
1006	总直流功率	W
1005	总直流电流	A
1009	第1路电流	A
1010	第2路电流	A
1011	第3路电流	A
1012	第4路电流	A
1013	第5路电流	A
1014	第6路电流	A
1015	第7路电流	A
1016	第8路电流	A
1017	第9路电流	A
1018	第10路电流	A
1019	第11路电流	A
1020	第12路电流	A
1021	第13路电流	A
1022	第14路电流	A
1023	第15路电流	A
1024	第16路电流	A
1025	第17路电流	A
1026	第18路电流	A
1027	第19路电流	A
1028	第20路电流	A
1029	第21路电流	A
1030	第22路电流	A
1031	第23路电流	A
1032	第24路电流	A
环境检测仪	2003	平面瞬时辐照	W/㎡
2001	平面日辐射量	Wh/㎡
2002	平面总辐射量	Wh/㎡
2007	斜面瞬时辐照	W/㎡
2005	斜面日辐射量	Wh/㎡
2006	斜面总辐射量	Wh/㎡
2009	环境温度	℃
2010	组件温度	℃
2016	风速	m/s
2011	风速等级	
2012	风向度数	°
2014	大气压力	hPa
2015	环境湿度	%RH
2022	雨量	mm
2026	降水量	mm
2100	温度1（背板温度）	℃
2101	温度2	℃
2102	温度3	℃
2103	温度4	℃
2104	温度5	℃
2105	露点	
2106	土湿1	
2107	土湿2	
2108	土湿3	
2109	CO₂	
2110	蒸发	
2111	总辐射1瞬时值	
2114	总辐射2瞬时值	
2112	散射辐射瞬时值	
2113	直接辐射瞬时值	
2115	净辐射瞬时值	
2116	光合辐射瞬时值	
2117	紫外辐射瞬时值	
2118	风向瞬时值	
2119	风速瞬时值	
2120	2分钟风速	
2121	10分钟风速	
2122	雨量时间间隔累计值	
2123	日照时间间隔累计值	
2124	总辐射1时间间隔累计值	
2127	总辐射2时间间隔累计值	
2125	散射辐射时间间隔累计值	
2126	直接辐射时间间隔累计值	
2128	净辐射时间间隔累计值	
2129	光合辐射时间间隔累计值	
2130	紫外辐射时间间隔累计值	
2131	雨量日累计	
2132	日照日累计	
2133	总辐射1日累计值	
2136	总辐射2日累计值	
2134	散射辐射日累计值	
2135	直接辐射日累计值	
2137	净辐射日累计值	
2138	光合辐射日累计值	
2139	紫外辐射日累计值	
电表	8030	正向有功电度	Wh
8031	反向有功电度	Wh
8062	日正向有功电度	Wh
8063	日反向有功电度	Wh
8032	正向无功电度	varh
8033	反向无功电度	varh
8034	峰正向有功电度	Wh
8035	峰反向有功电度	Wh
8038	谷正向有功电度	Wh
8039	谷反向有功电度	Wh
8042	平正向有功电度	Wh
8043	平反向有功电度	Wh
8058	尖正向有功电度	Wh
8059	尖反向有功电度	Wh
8036	峰正向无功电度	Wh
8037	峰反向无功电度	Wh
8040	谷正向无功电度	Wh
8041	谷反向无功电度	Wh
8044	平正向无功电度	Wh
8045	平反向无功电度	Wh
8060	尖正向无功电度	Wh
8061	尖反向无功电度	Wh
8000	A相电压	V
8001	B相电压	V
8002	C相电压	V
8003	A-B线电压	V
8004	B-C线电压	V
8005	C-A线电压	V
8006	A相电流	A
8007	B相电流	A
8008	C相电流	A
8064	频率	Hz
8018	电表有功功率	W
8022	无功功率	var
8014	功率因数	
8026	视在功率	VA
8076	电表A相有功功率	W
8077	电表B相有功功率	W
8078	电表C相有功功率	W
8084	日直接消耗电量	Wh
8085	总直接消耗电量	Wh
通信装置	10555	AI电压信号1	V
10557	AI电压信号2	V
10559	AI电压信号3	V
10561	AI电压信号4	V
10575	AI电流信号1	mA
10576	AI电流信号2	mA
10577	AI电流信号3	mA
10578	AI电流信号4	mA
10563	PT信号1	℃
10565	PT信号2	℃
10567	DO信号1	
10569	DO信号2	
10571	DO信号3	
10573	DO信号4	
10026	总功率	W
10046	总无功功率	var
10587	总有功功率	W
10510	移动网络信号强度	
10511	WLAN信号强度	
10028	总发电量	Wh
储能逆变器	13011	有功功率	W
13012	总无功功率	var
13003	总直流功率	W
13013	总功率因数	
13157	A相电压	V
13158	B相电压	V
13159	C相电压	V
13008	A相电流	A
13009	B相电流	A
13010	C相电流	A
13160	方阵绝缘阻抗	kΩ
13007	电网频率	Hz
18065	离网口A相功率	W
18066	离网口B相功率	W
18067	离网口C相功率	W
18068	离网口总功率	W
18062	离网口A相电流	A
18063	离网口B相电流	A
18064	离网口C相电流	A
13020	总运行时间	H
13112	日PV发电量	Wh
13134	总PV发电量	Wh
13187	交流电压	V
13188	交流电流	A
13004	A-B线电压	V
13005	B-C线电压	V
13006	C-A线电压	V
13019	机内空气温度	℃
13161	母线电压	V
13001	MPPT1电压	V
13105	MPPT2电压	V
13107	MPPT3电压	V
13109	MPPT4电压	V
13002	MPPT1电流	A
13106	MPPT2电流	A
13108	MPPT3电流	A
13110	MPPT4电流	A
13122	今日馈网	Wh
13125	累计馈网	Wh
13147	今日取电	Wh
13148	累计取电	Wh
13149	电网取电功率	W
13121	馈网功率	W
13173	今日PV馈网	Wh
13175	累计PV馈网	Wh
13141	电池电量	
13029	今日电池放电	Wh
13028	今日电池充电	Wh
13138	电池电压	V
13139	电池电流	A
13035	累计电池放电	Wh
13034	累计电池充电	Wh
13142	电池健康度	
13143	电池温度	℃
13162	最大充电电流(BMS)	A
13163	最大放电电流(BMS)	A
13174	今日PV电池充电	Wh
13176	累计PV电池充电	Wh
13126	电池充电功率	W
13150	电池放电功率	W
13199	日负载用电	Wh
13137	总直接消耗电量	Wh
13119	负载功率	W
13130	总负载用电	Wh
13116	日直接消耗电量	Wh
13144	日自发自用率	
13016	总充电时间	H
13017	总放电时间	H
13018	总视在功率	VA
13023	日充电时间	H
13024	日放电时间	H
13118	年直接消耗电量	Wh
13165	MDSP离网启机状态	
13166	SDSP工作模式	
13167	SDSP离网启机状态	
13168	DI状态	
13169	电池电压（BMS）	V
13170	电池SOC（BMS）	
13171	EMS状态	
13172	日自给自足率	
13140	电池容量(kWh)	Wh
18075	通道二总视在功率	VA
18076	通道二A相视在功率	VA
18077	通道二B相视在功率	VA
18078	通道二C相视在功率	VA
18079	通道二总有功功率	W
18080	通道二A相有功功率	W
18081	通道二B相有功功率	W
18082	通道二C相有功功率	W
18083	通道二总无功功率	var
18084	通道二A相无功功率	var
18085	通道二B相无功功率	var
18086	通道二C相无功功率	var
18087	通道二功率因数	
18088	通道二总取电电量	Wh
18089	通道二A相取电电量	Wh
18090	通道二B相取电电量	Wh
18091	通道二C相取电电量	Wh
18092	通道二总馈网电量	Wh
18093	通道二A相馈网电量	Wh
18094	通道二B相馈网电量	Wh
18095	通道二C相馈网电量	Wh
18103	离网口A相电压	V
18104	离网口B相电压	V
18105	离网口C相电压	V
18108	电表A相电压	V
18109	电表B相电压	V
18110	电表C相电压	V
13146	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网直流充电，20-微网运行	
通讯模块	23001	无线信号强度	
23014	WLAN信号强度	
23008	卡号	
电池	58601	电池电压	V
58602	电池电流	A
58603	电池温度	℃
58604	电池剩余电量	
58605	电池健康度	
58606	累计电池充电	Wh
58607	累计电池放电	Wh
58608	电池运行状态（0:空闲,1:待机,2:运行,3:故障,4:关机,5:升级,6:校正,7:测试）	
58609	标准健康状态	
58610	电芯电压最大值	mV
58611	电芯电压最大值位置	
58612	电芯电压最小值	mV
58613	电芯电压最小值位置	
58614	模组温度最高值	℃
58615	模组温度最高值位置	
58616	模组温度最低值	℃
58617	模组温度最低值位置	
58618	模组1电芯电压最大值	mV
58619	模组2电芯电压最大值	mV
58620	模组3电芯电压最大值	mV
58621	模组4电芯电压最大值	mV
58622	模组5电芯电压最大值	mV
58623	模组6电芯电压最大值	mV
58624	模组7电芯电压最大值	mV
58625	模组8电芯电压最大值	mV
58626	模组1电芯电压最小值	mV
58627	模组2电芯电压最小值	mV
58628	模组3电芯电压最小值	mV
58629	模组4电芯电压最小值	mV
58630	模组5电芯电压最小值	mV
58631	模组6电芯电压最小值	mV
58632	模组7电芯电压最小值	mV
58633	模组8电芯电压最小值	mV
58635	直流接触器状态	
58636	故障模组位置	
EMS	24620	储能日充电量	Wh
24622	储能总充电量	Wh
24621	储能日放电量	Wh
24623	储能总放电量	Wh
24624	光伏有功功率	W
24625	储能有功功率	W
24626	电网有功功率	W
24627	光伏日发电量	Wh
24628	光伏总发电量	Wh
24629	储能SOC	%
24630	储能剩余电量	Wh
24631	有功负载	W
LC	59502	软件版本	
59546	日充电量	Wh
59535	总充电量	Wh
59547	日放电量	Wh
59536	总放电量	Wh
59541	总有功功率	W
59542	总无功功率	var
59551	工作模式	
59552	系统工作状态（0:初始状态,1:自检,2:自检失败,3:启动中,4:运行,5:告警运行,6:待机,7:停机中,8:停机,9:紧急停机,10:故障停机）	
59705	设备S/N	
PCS	44010	整机总有功功率	W
44011	整机总无功功率	var
44012	整机功率因数	
44029	整机电网频率	Hz
44025	工作模式	
44231	运行状态（0:并网运行,4096:离网运行,4608:初始待机,5632:启动中,37120:告警运行,33024:降额运行,5120:热待机,4864:按键关机,21760:故障停机,5376:紧急停机,12288:零功率状态运行,4610:运行）	
44244	机内空气温度	℃
44803	设备S/N	
44823	PCS-DSP版本号	
44824	PCS-CPLD版本号	
CMU	59002	总电压	
59003	总电流	
59004	SOC	
59006	电池总容量	
59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59403	软件版本	
BSC	59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59064	最高电芯电压位置(#BMU~#Cell)	
59065	最低电芯电压位置(#BMU~#Cell)	
59066	最高电芯温度位置(#BMU~#Cell)	
59067	最低电芯温度位置(#BMU~#Cell)	
充电桩	33708	充电功率	kW
33722	最小充电功率	kW
33723	最大充电功率	kW
33702	A相充电电压	V
33704	B相充电电压	V
33706	C相充电电压	V
33710	CP电压	V
33707	C相充电电流	A
33705	B相充电电流	A
33703	A相充电电流	A
33728	最大充电电流	A
33729	最小充电电流	A
33716	充电状态（空闲(未插枪):1-- 待机(已插枪):2--充电中:3--充电暂停(桩端):4--充电暂停(车端):5--充电完成:6--预约:7--禁用:8--故障:9）	
微逆






51301	运行状态（21760:故障停机,0:并网运行,1024:维护模式运行,2048:强制模式运行,4096:离网运行,8192:开环,4608:初始待机,32768:停机,5120:待机,5632:启动中,33024:降额运行,33280:调度运行,4369:初始状态,4864:按键关机,37120:告警运行）	
51346	当日发电	Wh
51302	总发电量	Wh
51303	总有功功率	W
51304	总无功功率	var
51305	总直流功率	W
51306	总视在功率	VA
51307	总功率因数	
51308	电网频率	Hz
51309	交流电压	V
51312	交流电流	A
51315	PV1电压	V
51317	PV2电压	V
51319	PV3电压	V
51321	PV4电压	V
51323	PV5电压	V
51325	PV6电压	V
51316	PV1电流	A
51318	PV2电流	A
51320	PV3电流	A
51322	PV4电流	A
51324	PV5电流	A
51326	PV6电流	A
51333	PV1功率	W
51334	PV2功率	W
51335	PV3功率	W
51336	PV4功率	W
51337	PV5功率	W
51338	PV6功率	W
51347	PV1当日发电	Wh
51348	PV2当日发电	Wh
51349	PV3当日发电	Wh
51350	PV4当日发电	Wh
51351	PV5当日发电	Wh
51352	PV6当日发电	Wh
51339	PV1累计发电	Wh
51340	PV2累计发电	Wh
51341	PV3累计发电	Wh
51342	PV4累计发电	Wh
51343	PV5累计发电	Wh
51344	PV6累计发电	Wh
查询设备的属性测点数据
Post
/openapi/getDevPropertyPointValue

查询电站下N个同一种类型的设备的指定的属性测点的值。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
device_type
Integer
是
1
设备类型
point_id_list
List
是
["202"]
测点id集合，具体开放测点定义信息通过常用遥测测点获取。
ps_id
Integer
是
1564425
电站ID
ps_key_list
List
是
["1564425_1_1_2"]
设备ps_key集合（相同类型的设备）
{
	"device_type":1,
	"point_id_list":[
		"202"
	],
	"ps_key_list":[
		"1564425_1_1_2"
	],
	"ps_id":"1564425"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241127f4ad4f8bb03430bb72919a20
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.code
String
1
结果编码： 1：查询成功 2：入参数据为空 3：用户下无该电站 4：未查询到数据
result_data.property_point_value_list
List
--
设备的属性测点数据
result_data.property_point_value_list.device_type
Integer
1
设备类型
result_data.property_point_value_list.property_code
String
202
属性测点id
result_data.property_point_value_list.property_value
String
1000
属性测点值
result_data.property_point_value_list.ps_key
String
1564425_1_1_2
设备ps_key
result_data.property_point_value_list.unit
String
Wp
属性值对应的单位
result_data.property_point_value_list.uuid
Integer
13169047
设备UUID
2.1 成功示例
{
	"req_serial_num":"20241127f4ad4f8bb03430bb72919a20",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"code":"1",
		"property_point_value_list":[
			{
				"property_code":"202",
				"unit":"Wp",
				"ps_key":"1564425_1_1_2",
				"device_type":1,
				"property_value":"10000",
				"uuid":13169047
			}
		]
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}



查询设备的故障告警信息
Post
/openapi/getFaultAlarmInfo

查询设备的故障告警信息。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
curPage
String
是
1
页码
share_type
String
否
0,1,2
电站的分享类型： 1：查询具有浏览权限的分享电站 2：查询具有管理权限的分享电站 0：查询本人电站 多个类型使用逗号隔开传入，默认查询所有
size
String
是
100
每页大小
fault_code
String
否
60064.202411.47b8b34242077
故障唯一标识，如果传入，则查询该故障告警的信息
fault_name
String
否
Grid Power Outage
故障名称（不为空时进行模糊查询）
startTime
String
否
2024-11-24 16:33:12
开始时间（格式：yyyyMMddHHmm）可为空。注：查询process_status=9或999的故障列表的时候，时间区间只能查询某个月的数据，不能跨月查询。不传入时间，默认查询当月的故障。
endTime
String
否
2024-11-27 16:38:12
结束时间（格式：yyyyMMddHHmm）可为空。 注：查询process_status=9或999的故障列表的时候，时间区间只能查询某个月的数据，不能跨月查询。不传入时间，默认查询当月的故障。
process_status
String
否
999
故障状态： 8：未关闭 9：已关闭 999: 未关闭和已关闭（不能跨月查询） 如果该字段为空，则查询未关闭的故障
fault_type
String
否
1,2,3,4
故障类型： 1：故障 2：告警 3：提示 4：建议 （传多个用逗号分割）
fault_level
String
否
1,2,3,4
故障级别： 1：重要 2：次要 3：一般 4：轻微 (传多个用逗号分割）
ps_id
String
否
1307933
电站id (ps_id不传时默认查询所有已授权电站的故障信息)
ps_key
String
否
1307933_1_1_1
设备ps_key
{
	"startTime":"2024-11-24 16:33:12",
	"fault_type":"1,2,3,4",
	"fault_level":"1,2,3,4",
	"curPage":1,
	"size":100,
	"ps_id":1307933,
	"ps_key":"1307933_1_1_1",
	"fault_code":"60064.202411.47b8b34242077",
	"fault_name":"系统故障",
	"share_type":"0,1,2",
	"process_status":"999",
	"endTime":"2024-11-27 16:38:12"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202411278d234adcbfc4d32b059fce33
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.pageList
List
--
故障列表
result_data.pageList.create_time
String
2022-09-28 14:15:54
故障发生时间 格式：yyyy-MM-dd HH:mm:ss
result_data.pageList.device_model_code
String
SG17RT-20
设备型号
result_data.pageList.device_name
String
SG17RT-20(COM1-001)_001_001
设备名称
result_data.pageList.fault_code
String
60064.202411.613e3b0521556
故障唯一id
result_data.pageList.fault_desc
String
Short-circuit, open loop, or low current
故障描述
result_data.pageList.fault_level
Integer
1
故障级别： 1：重要 2：次要 3：一般 4：轻微 (传多个用逗号分割）
result_data.pageList.fault_name
String
Grid Power Outage
故障名称
result_data.pageList.fault_type
Integer
1
故障类型： 1：故障 2：告警 3：提示 4：建议 （传多个用逗号分割）
result_data.pageList.fault_type_code
Integer
60005
故障类型编码
result_data.pageList.fault_reason
String
714
设备真实故障码（多个用“|”分隔）
result_data.pageList.over_time
String
2024-11-27 13:06:21
故障的恢复时间 格式：yyyy-MM-dd HH:mm:ss
result_data.pageList.process_status
Integer
9
故障处理状态: 1：未确认 2：待处理 3：处理中 4：已解决 9：已关闭
result_data.pageList.ps_id
Integer
1482711
电站ID
result_data.pageList.ps_key
String
1482711_1_1_1
设备ps_key
result_data.pageList.ps_name
String
PlantA
电站名称
result_data.pageList.type_name
String
Inverter
设备类型名称
result_data.pageList.uuid
Integer
36211221
设备UUID
result_data.pageList.grid_connection_status
Integer
1
是否并网故障，0否，1是
result_data.rowCount
Integer
1
总数
2.1 成功示例
{
	"req_serial_num":"202411278d234adcbfc4d32b059fce33",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"pageList":[
			{
				"ps_id":1307933,
				"ps_key":"1307933_1_1_1",
				"fault_type_code":60064,
				"fault_code":"60064.202411.47b8b34242077",
				"fault_type":1,
				"fault_level":1,
				"fault_desc":"",
				"process_status":1,
				"create_time":"2024-11-27 07:42:39",
				"process_time":20241127163323,
				"fault_reason":"20|24|25|200",
				"grid_connection_status":1,
				"device_model_code":"SG30T-CN",
				"device_model":"SG30T-CN",
				"device_name":"逆变器1",
				"device_type":1,
				"ps_name":"云龙-长新乡-永香村永登组36号",
				"uuid":12210669,
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}



查询阳光云开放的测点定义信息
Post
/openapi/getOpenPointInfo

根据设备类型查询该类型设备开放的遥测、遥信、属性测点信息,同时支持根据设备类型和设备型号ID查询该型号设备支持的开放遥测测点信息。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
curPage
Integer
是
1
页码
device_type
String
是
1
设备类型
size
Integer
是
999
每页大小
type
Integer
是
2
测点类型： 1：遥信测点 2：遥测测点 5：属性测点
device_model_id
String
是
367701
设备型号ID 查询遥测测点信息时，如果传入该参数则表示根据型号ID查询该型号支持的遥测测点信息，如果不传入该参数则查询该类型设备的所有开放测点
{
	"device_type":1,
	"type":2,
	"curPage":1,
	"size":999,
	"device_model_id":"367701"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
2024112717964c0f8986057ee771ddb6
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.pageList
List
--
测点信息
result_data.pageList.device_type
Integer
1
设备类型
result_data.pageList.open_point_remark
String
--
测点说明信息
result_data.pageList.point_id
Integer
1
测点ID
result_data.pageList.point_name
String
Plant Equivalent Hours
测点名称
result_data.pageList.show_unit
String
kWh
测点单位
result_data.pageList.storage_unit
String
Wh
测点数据存储单位（遥测和属性测点才有该出参）
result_data.rowCount
Integer
540
总数
2.1 成功示例
{
	"req_serial_num":"2024112717964c0f8986057ee771ddb6",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"rowCount":540,
		"pageList":[
			{
				"point_id":1,
				"open_point_remark":null,
				"storage_unit":"Wh",
				"show_unit":"kWh",
				"device_type":1,
				"point_name":"当日发电"
			},
			{
				"point_id":2,
				"open_point_remark":null,
				"storage_unit":"Wh",
				"show_unit":"kWh",
				"device_type":1,
				"point_name":"总发电量"
			},
			{
				"point_id":3,
				"open_point_remark":null,
				"storage_unit":"h",
				"show_unit":"h",
				"device_type":1,
				"point_name":"总并网运行时间"
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}

查询用户下设备列表
Post
/openapi/getDeviceListByUser

查询用户下设备列表
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
curPage
String
是
1
页码
size
String
是
100
每页大小
ps_id
String
否
7025**960
电站ID
is_virtual_unit
String
否
0
是否是查询虚拟设备，1：查询的是虚拟设备，0：查询的是物理设备，默认为0，即表示查询物理设备，电站、并网点、单元都属于虚拟设备
device_type_list
List
否
--
设备类型列表，限定条件，为空，查看全部 如： 11：电站、 1：逆变器、 3：并网点、 17：单元。具体参考附录中的设备类型定义
rel_state
String
否
1
设备认领状态：0：未认领，1：认领
is_get_firmware_version
String
否
0
是否需要获取设备的固件版本信息 1：需要、0：不需要，默认不需要
share_type
String
否
0,1,2
电站的分享类型： 1：查询具有浏览权限的分享电站 2：查询具有管理权限的分享电站 0：查询本人电站 多个类型使用逗号隔开传入，默认查询所有
{
	"curPage":"1",
	"size":"100"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241128bff64b68967f59380cba1e34
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.pageList
List
--
分页数据
result_data.pageList.chnnl_id
Integer
7
设备通道ID
result_data.pageList.communication_dev_sn
String
A22**416266
设备对应的通信设备的SN
result_data.pageList.dev_fault_status
Integer
4
设备当前故障状态设备故障状态：1：故障，2：告警，4：正常
result_data.pageList.dev_status
String
1
设备当前在线离线状态：0：离线，1：在线
result_data.pageList.device_code
Integer
1
设备地址编码
result_data.pageList.device_model_code
String
SG110CX-P2-CN
设备型号名称
result_data.pageList.device_model_id
Integer
346830
设备型号ID
result_data.pageList.device_name
String
1NB1
设备名称
result_data.pageList.device_sn
String
A2271**9433
设备S/N
result_data.pageList.device_type
Integer
1
设备类型编码
result_data.pageList.factory_name
String
Sunshine Power Co., Ltd
生产厂家
result_data.pageList.ps_id
Integer
654751
电站ID
result_data.pageList.ps_key
String
654751_1_1_7
设备的ps_key(查询设备数据需要用到)
result_data.pageList.rel_state
Integer
1
设备认领状态：0：未认领，1：认领
result_data.pageList.type_name
String
Home Energy Manager
设备类型名称
result_data.pageList.uuid
Integer
2024**5175
设备UUID
result_data.rowCount
Integer
7
记录数
2.1 成功示例
{
	"req_serial_num":"20241128bff64b68967f59380cba1e34",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"pageList":[
			{
				"chnnl_id":7,
				"type_name":"逆变器",
				"ps_key":"654751_1_1_7",
				"device_sn":"A2280416266",
				"dev_status":"1",
				"device_type":1,
				"factory_name":"阳光电源股份有限公司",
				"uuid":3577419,
				"grid_connection_date":"2022-08-19 18:17:49",
				"device_name":"1NB1",
				"dev_fault_status":4,
				"rel_state":1,
				"device_code":1,
				"ps_id":654751,
				"device_model_id":346830,
				"communication_dev_sn":"A2271449433",
				"device_model_code":"SG110CX-P2-CN"
			},
			{
				"chnnl_id":13,
				"type_name":"逆变器",
				"ps_key":"654751_1_1_13",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}

根据设备SN查询对应的通信设备信息
Post
/openapi/getCommunicationDevInfoByDevSn

根据设备SN查询对应的通信设备信息
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
dev_sn
String
是
A2451509521
设备SN
share_type
String
否
0
设备sn对应电站的分享类型： 1：查询具有浏览权限的分享电站 2：查询具有管理权限的分享电站 0：查询本人电站 多个类型使用逗号隔开传入，默认查询本人电站
{
	"dev_sn":"A2451509521"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240826fbed497cbc7b3b879802db5c
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.device_model_code
String
iHomeManager
设备型号名称
result_data.ps_id
Integer
700666130
电站ID
result_data.ps_key
String
700666130_64_247_1
设备ps_key
result_data.ps_name
String
PlantA
电站名称
result_data.sn
String
A2462**0013
设备对应的通信设备的SN
result_data.uuid
Integer
2024525175
设备UUID
2.1 成功示例
{
	"req_serial_num": "20230114c7b143df8b38b50756acee62",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"device_model_code": "iHomeManager",
		"ps_id": 747,
		"ps_key": "747_22_247_1",
		"ps_name": "PlantA",
		"sn": "A24627C0013",
		"uuid": 40712451
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


查询光伏逆变器的实时测点数据
Post
/openapi/getPVInverterRealTimeData

根据光伏逆变器的ps_key或SN查询实时测点数据(数据的单位均为最小基本单位)。 注：该接口返回的数据的单位都是最小单位，如发电量数据对应单位是wh，功率数据对应的单位是w，电流对应单位是A，电压对应单位是V。该接口只针对光伏逆变器，其他类型的设备可以通过2.7查询同类型设备的历史测点分钟级数据接口传入最近的时间获取。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_key_list
List
否
["700666130_22_247_3","700666130_22_247_2","700666130_14_1_2"]
设备ps_key集合（相同类型的设备）
sn_list
List
否
['A21B1801347','A29B1902347']
sn集合，ps_key_list与sn_list只需传入一个
{
		"A2492001243",
		"A2492001249",
		"A2492001265",
		"A2492001268",
		"A2492001270",
		"A2492001272",
		"A2492001273",
		"A2492001299",
		"A2492001314",
		"A2492001336",
		"A2492001344",
		"A2492001358",
		"A2492001383",
		"A2492001395",
		"A2492001400",
		"A2492001428",
		"A2492001452",
		"A2492001465",
		"A2492001473",
		"A2492001521",
		"A2492001540",
		"A2492013176",
		"A2492013179",
		"A2492013181",
		"A2492013182",
		"A2492013184",
		"A2492013186",
		"A2492013215",
		"A2492013223",
		"A2492013224",
		"A2492013237",
		"A2492013247",
		"A2492013258",
		"A2492013259",
		"A2492013261",
		"A2492013278",
		"A2492013284",
		"A2492013285",
		"A2492013289",
		"A2492013305",
		"A2492013337",
		"A2492013346",
		"A2492013365",
		"A2492013391",
		"A2492013397",
		"A2492013417",
		"A2492013426",
		"A2492013429",
		"A2492013433",
		"A2492013435",
		"A2492013439",
		"A2492013440",
		"A2492013457",
		"A2492013462",
		"A2492013465",
		"A2492013466",
		"A2492013478",
		"A2492013484",
		"A2492013509",
		"A2492013511",
		"A2492013512",
		"A2492013515",
		"A2492013516",
		"A2492013517",
		"A2492013518",
		"A2492013520",
		"A2492013524",
		"A2492013525",
		"A2492013536",
		"A2492013549",
		"A2492013580",
		"A2492013592",
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202411284aa542cb81d57eb3a4aac320
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.device_point_list
List
--
每个设备测点值集合
result_data.device_point_list.device_point
Map
--
测点集合
result_data.device_point_list.device_point.communication_dev_sn
String
A23519**928
设备对应的通信设备的SN
result_data.device_point_list.device_point.dev_fault_status
Integer
4
设备当前故障状态设备故障状态：1：故障，2：告警，4：正常
result_data.device_point_list.device_point.dev_status
Integer
1
设备当前在线离线状态：0：离线，1：在线
result_data.device_point_list.device_point.device_name
String
Hybrid Inverter2
设备名称
result_data.device_point_list.device_point.device_sn
String
A2351907928
设备SN
result_data.device_point_list.device_point.device_time
String
20240822195000
设备数据更新时间
result_data.device_point_list.device_point.p1
String
79
逆变器日发电量
result_data.device_point_list.device_point.p10
String
87
MPPT3电流
result_data.device_point_list.device_point.p100
String
492
组串5电压
result_data.device_point_list.device_point.p101
String
94
组串6电压
result_data.device_point_list.device_point.p102
String
35
组串7电压
result_data.device_point_list.device_point.p103
String
24
组串8电压
result_data.device_point_list.device_point.p104
String
27
组串9电压
result_data.device_point_list.device_point.p105
String
46
组串10电压
result_data.device_point_list.device_point.p14
String
353
总直流功率
result_data.device_point_list.device_point.p15
String
41
A-B线电压
result_data.device_point_list.device_point.p16
String
45
B-C线电压
result_data.device_point_list.device_point.p17
String
331
C-A线电压
result_data.device_point_list.device_point.p18
String
417
A相电压
result_data.device_point_list.device_point.p19
String
46
B相电压
result_data.device_point_list.device_point.p2
String
81
总发电量
result_data.device_point_list.device_point.p20
String
324
C相电压
result_data.device_point_list.device_point.p21
String
486
A相电流
result_data.device_point_list.device_point.p22
String
72
B相电流
result_data.device_point_list.device_point.p23
String
378
C相电流
result_data.device_point_list.device_point.p24
String
11
总有功功率
result_data.device_point_list.device_point.p25
String
483
总无功功率
result_data.device_point_list.device_point.p26
String
0
总功率因数
result_data.device_point_list.device_point.p27
String
0
电网频率
result_data.device_point_list.device_point.p304
String
1
设备故障状态
result_data.device_point_list.device_point.p313
String
23
组串19电流
result_data.device_point_list.device_point.p314
String
13
组串20电流
result_data.device_point_list.device_point.p315
String
15
组串21电流
result_data.device_point_list.device_point.p316
String
46
组串22电流
result_data.device_point_list.device_point.p317
String
73
组串23电流
result_data.device_point_list.device_point.p318
String
24
组串24电流
result_data.device_point_list.device_point.p319
String
241
组串25电流
result_data.device_point_list.device_point.p320
String
15
组串26电流
result_data.device_point_list.device_point.p321
String
52
组串27电流
result_data.device_point_list.device_point.p322
String
62
组串28电流
result_data.device_point_list.device_point.p323
String
15
组串29电流
result_data.device_point_list.device_point.p324
String
16
组串30电流
result_data.device_point_list.device_point.p325
String
53
组串31电流
result_data.device_point_list.device_point.p326
String
25
组串32电流
result_data.device_point_list.device_point.p4
String
56
机内空气温度
result_data.device_point_list.device_point.p43
String
25
总视在功率
result_data.device_point_list.device_point.p45
String
35
MPPT4电压
result_data.device_point_list.device_point.p46
String
26
MPPT4电流
result_data.device_point_list.device_point.p47
String
37
MPPT5电压
result_data.device_point_list.device_point.p48
String
8
MPPT5电流
result_data.device_point_list.device_point.p49
String
13
MPPT6电压
result_data.device_point_list.device_point.p5
String
16
MPPT1电压
result_data.device_point_list.device_point.p50
String
14
MPPT6电流
result_data.device_point_list.device_point.p51
String
13
MPPT7电压
result_data.device_point_list.device_point.p52
String
15
MPPT7电流
result_data.device_point_list.device_point.p53
String
5
MPPT8电压
result_data.device_point_list.device_point.p54
String
36
MPPT8电流
result_data.device_point_list.device_point.p55
String
24
MPPT9电压
result_data.device_point_list.device_point.p56
String
26
MPPT9电流
result_data.device_point_list.device_point.p57
String
63
MPPT10电压
result_data.device_point_list.device_point.p58
String
26
MPPT10电流
result_data.device_point_list.device_point.p6
String
26
MPPT1电流
result_data.device_point_list.device_point.p7
String
17
MPPT2电压
result_data.device_point_list.device_point.p70
String
38
组串1电流
result_data.device_point_list.device_point.p71
String
52
组串2电流
result_data.device_point_list.device_point.p72
String
31
组串3电流
result_data.device_point_list.device_point.p73
String
42
组串4电流
result_data.device_point_list.device_point.p74
String
53
组串5电流
result_data.device_point_list.device_point.p75
String
52
组串6电流
result_data.device_point_list.device_point.p76
String
21
组串7电流
result_data.device_point_list.device_point.p77
String
15
组串8电流
result_data.device_point_list.device_point.p7708
String
16
组串33电流
result_data.device_point_list.device_point.p7710
String
16
组串34电流
result_data.device_point_list.device_point.p7712
String
171
组串35电流
result_data.device_point_list.device_point.p7714
String
8
组串36电流
result_data.device_point_list.device_point.p7716
String
41
组串37电流
result_data.device_point_list.device_point.p7718
String
47
组串38电流
result_data.device_point_list.device_point.p7720
String
37
组串39电流
result_data.device_point_list.device_point.p7722
String
21
组串40电流
result_data.device_point_list.device_point.p78
String
37
组串9电流
result_data.device_point_list.device_point.p79
String
32
组串10电流
result_data.device_point_list.device_point.p8
String
83
MPPT2电流
result_data.device_point_list.device_point.p80
String
1
组串11电流
result_data.device_point_list.device_point.p81
String
4
组串12电流
result_data.device_point_list.device_point.p82
String
5
组串13电流
result_data.device_point_list.device_point.p83
String
26
组串14电流
result_data.device_point_list.device_point.p84
String
73
组串15电流
result_data.device_point_list.device_point.p85
String
25
组串16电流
result_data.device_point_list.device_point.p87
String
26
月发电量
result_data.device_point_list.device_point.p88
String
17
年发电量
result_data.device_point_list.device_point.p9
String
14
MPPT3电压
result_data.device_point_list.device_point.p92
String
62
组串17电流
result_data.device_point_list.device_point.p93
String
35
组串18电流
result_data.device_point_list.device_point.p96
String
21
组串1电压
result_data.device_point_list.device_point.p97
String
25
组串2电压
result_data.device_point_list.device_point.p98
String
16
组串3电压
result_data.device_point_list.device_point.p99
String
12
组串4电压
result_data.device_point_list.device_point.ps_id
Integer
702966130
电站ID
result_data.device_point_list.device_point.ps_key
String
701966430_14_1_2
设备的ps_key
result_data.device_point_list.device_point.uuid
Integer
2924525197
设备UUID
result_data.fail_ps_key_list
List
["700926130_22_247_2","700926130_22_247_3"]
不合法的ps_key集合
result_data.fail_sn_list
List
["A2492001119","A2492001137","A2492001145","A2492001149"]
不合法的SN集合 说明：根据SN集合查询的时候才会有该出参
2.1 成功示例
{
	"req_serial_num":"202411284aa542cb81d57eb3a4aac320",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"fail_sn_list":[
			"A2492001119",
			"A2492001137",
			"A2492001145",
			"A2492001149",
			"A2492001164",
			"A2492001165",
			"A2492001178",
			"A2492001185",
			"A2492001192",
			"A2492001215",
			"A2492001221",
			"A2492001228",
			"A2492001239",
			"A2492001243",
			"A2492001249",
			"A2492001265",
			"A2492001268",
			"A2492001270",
			"A2492001272",
			"A2492001273",
			"A2492001299",
			"A2492001314",
			"A2492001336",
			"A2492001344",
			"A2492001358",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}

查询API调用情况
Post
/openapi/getOpenApiCallInfo

查询API调用情况
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
appkey
String
是
D8D0C0CCD201D4930C4C13726E734D5C
授权码
token
String
是
350943_dfe4378d1a2d45939e2469a785081d16
认证成功后返回token
{
	"token":"350943_dfe4378d1a2d45939e2469a785081d16",
	"appkey":"D8D0C0CCD201D4930C4C13726E734D5C"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241121641145ea9bf782eb75c377ca
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.curr_hour_accessed_times
String
4021
当前小时已经访问的次数
result_data.per_day_access_times_config
String
345600
配置的今天可以访问的总次数
result_data.per_hour_access_times_config
List
--
配置的每个小时可以调用的最大次数
result_data.per_hour_access_times_config.hour
String
4
小时
result_data.per_hour_access_times_config.max_call_times
Integer
14400
可以调用的最大次数
result_data.per_hour_residue_times
List
--
今天每个小时对应的剩余调用次数
result_data.per_hour_residue_times.hour
String
3
小时
result_data.per_hour_residue_times.times
String
14400
该小时的剩余调用次数
result_data.today_accessed_times
String
59433
今天已经访问的次数
2.1 成功示例
{
	"req_serial_num":"20241121641145ea9bf782eb75c377ca",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"per_day_access_times_config":"345600",
		"curr_hour_accessed_times":"4021",
		"today_accessed_times":"59433",
		"per_hour_access_times_config":[
			{
				"hour":"0",
				"max_call_times":14400
			},
			{
				"hour":"1",
				"max_call_times":14400
			},
			{
				"hour":"2",
				"max_call_times":14400
			},
			{
				"hour":"3",
				"max_call_times":14400
			},
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}



批量查询电站的基本信息
Post
/openapi/getBatchPsDetail

批量查询电站的基本信息
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_ids
String
否
700669800,700669628
电站id，多个之间用逗号隔开(最多支持查询20个，ps_ids和sns2个必须填写1个，同时传入时优先使用ps_ids查询，ps_ids为空时才会使用sns查询)
sns
String
否
A2360319347,A2410307309,A2361920595,A2352321024
通讯设备sn，多个之间用逗号隔开(最多支持查询20个，ps_ids为空时才会使用sns查询)
is_get_ps_remarks
String
是
1
是否获取电站的备注信息： 1：获取， 不传默认不获取
lang
String
是
_en_US
国际化语言
{
	"is_get_ps_remarks": "1",
	"lang": "_en_US"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
2024112850614aaaadf13ebba1dd5e4e
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.code
String
1
接口响应码，0-查询失败，接口异常，1-成功，3-入参中有user_id，并且user_id和token用户不一致，4-入参中ps_ids为空，通过sns没有查询到电站，5-查询电站数量或者sns超过最大限制，6-根据ps_ids没有查到电站的基本信息，7-入参ps_ids中的电站全部都不是当前用户下的电站
result_data.is_not_belong_to_user
List
["78925","678743"]
入参ps_ids中不属于当前用户下的电站id集合
result_data.dataList
List
--
电站基本信息集合
result_data.dataList.design_capacity
Integer
200000
装机功率，单位为Wp
result_data.dataList.alarm_count
Integer
0
告警数量
result_data.dataList.ps_key
String
789252_11_0_0
电站的ps_key
result_data.dataList.latitude
Num
11.875595
纬度
result_data.dataList.description
String
Rooftop power station
电站简介
result_data.dataList.ps_remarks
Map
Rooftop power station
电站备注信息（入参is_get_ps_remarks为1时返回）
result_data.dataList.ps_price_kwh
String
1
电站当前每kWh的电价
result_data.dataList.ps_fault_status
Integer
3
电站故障状态 1：故障，2：告警，4：正常
result_data.dataList.ps_type_name
String
Residential PV
电站类型名称
result_data.dataList.build_status
Integer
2
电站建设状态 0：未建，1：在建 2：并网，3：拟建，4：未接入
result_data.dataList.install_date
String
2024-04-19 12:26:00
建站日期
result_data.dataList.ps_type
Integer
4
电站类型：1：地面电站 3：分布式光伏 4：户用光伏 5：户用储能 6：村级电站 7：分布式储能 8：扶贫电站 9：风能电站 12：工商业储能
result_data.dataList.email
String
1553417357@gmail.com
业主用户的邮箱
result_data.dataList.longitude
Num
41.69395123697499
电站经度
result_data.dataList.param_income_unit_name
String
CNY
电价单位
result_data.dataList.ps_price
String
1
电站当前每Wh的电价
result_data.dataList.ps_name
String
PlantA
电站名称
result_data.dataList.share_user_type
String
1
电站的分享人类型：1：业主分享2：安装商分享 其他：非分享电站
result_data.dataList.share_type
String
0
电站的分享类型 1：分享类型（浏览权限）2：分享类型（管理权限）0：非分享电站（本人电站）
result_data.dataList.ps_current_time_zone
String
GMT+8
电站当前时区
result_data.dataList.user_moble_tel
String
185**561987
业主用户手机号码
result_data.dataList.ps_id
Integer
24312
电站ID
result_data.dataList.communication_dev_detail_list
List
--
电站的通信设备SN信息
result_data.dataList.communication_dev_detail_list.is_enable
Integer
1
SN状态：0：禁用，1：正常
result_data.dataList.communication_dev_detail_list.sn
String
A20***32682
SN
result_data.dataList.connect_type
Integer
2
并网类型：1：全额上网 2：自发自用，余电上网 3：自发自用，无馈网 4：离网
result_data.dataList.ps_status
Integer
1
电站状态 1：在线，0：离线
result_data.dataList.fault_count
Integer
0
故障数量
2.1 成功示例
{
    "req_serial_num": "2024112850614aaaadf13ebba1dd5e4e",
    "result_code": "1",
    "result_msg": "success",
    "result_data": {
        "code":"1",
        "is_not_belong_to_user":[
            "78925",
            "678743"
        ],
        "dataList": [
            {
                "design_capacity": 20.0,
                "alarm_count": 0,
                "ps_key": "789252_11_0_0",
                "latitude": 31.875595,
                "description": null,
                "ps_remarks":{
			        "remark1":"Rooftop power station",
			        "remark2":"",
			        "remark3":"",
			        "remark4":"",
			        "remark5":""
		        },
                "ps_price_kwh": "1",
                "ps_fault_status": 3,
2.2 失败示例
{
	"result_msg":"Unauthorized access",
	"result_data":null,
	"result_code":"E900"
}
2.3 错误码
错误码
描述
1
成功
0
查询失败，接口异常
4
入参中ps_ids为空，通过sns没有查询到电站
5
查询电站数量或者sns超过最大限制
6
根据ps_ids没有查到电站的基本信息
7
入参ps_ids中的电站均未授权




查询设备组串配置信息
Post
/openapi/getDeviceStringInfo

查询设备组串配置信息
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_key_list
List
是
["700666130_22_247_3","700666130_22_247_2","700666130_14_1_2"]
设备ps_key集合（相同类型的设备）
lang
String
是
_en_US
国际化语言
{
	"ps_key_list": [
		"700666130_22_247_3",
		"700666130_14_1_2"
	],
	"lang": "_en_US"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241128101d403b9bf6cffb674fc0d9
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.device_string_info
Map
--
组串信息
result_data.device_string_info.pv_count
String
2
组串数量
result_data.device_string_info.pv_string
List
--
组串配置信息
result_data.device_string_info.pv_string.pv_value
String
1
当前组串是否配置1:已配置，0:未配置
result_data.device_string_info.pv_string.pv_name
String
PV1
组串路数
result_data.fail_ps_key
List
["1057394_1_25_1_1111"]
失败的psKey
result_data.code
String
1
1：成功，0：失败
2.1 成功示例
{
    "req_serial_num": "20241128101d403b9bf6cffb674fc0d9",
    "result_code": "1",
    "result_msg": "success",
    "result_data": {
        "device_string_info": [
            {
                "pv_count": 2,
                "update_time": "2024-07-01 17:14:48",
                "ps_key": "342481895_1_1_1",
                "pv_string": [
                    {
                        "pv_value": "1",
                        "pv_name": "PV1"
                    },
                    {
                        "pv_value": "1",
                        "pv_name": "PV2"
                    }
                ]
            },
            {
                "pv_count": 2,
                "update_time": "2024-07-01 17:14:48",
                "ps_key": "342481899_1_1_1",
                "pv_string": [
                    {
                        "pv_value": "1",
                        "pv_name": "PV1"
                    },
                    {
                        "pv_value": "0",
                        "pv_name": "PV2"
                    }
                ]
            },
        ],
        "code": 1,
        "fail_ps_key": [
            "1057394_1_25_1_1111"
        ]
    },
    "exception_stack_trace": null
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


获取电站下优化器设备列表
Post
/openapi/getMlpeDeviceList

获取电站下优化器设备列表
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_id
String
是
700665973
电站ID
{
	"ps_id": "122334"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202411289fbe4453956dd608cb9b58c3
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.code
String
1
1：正常； 9：无权限
result_data.device_list
List
--
设备
result_data.device_list.ps_key
String
700665973_1_1_1
优化器的ps_key
result_data.device_list.sn
String
WL20**08191
优化器S/N
2.1 成功示例
{
	"req_serial_num": "20241128ce654a36888dae047164f430",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"device_list": [{
				"ps_key": "1122336553_41_10011_1",
				"sn": "VOPT001920101"
			},
			{
				"ps_key": "1122336553_41_20008_1",
				"sn": "VOPT001910203"
			},
			{
				"ps_key": "1122336553_41_20009_1",
				"sn": "VOPT001910204"
			},
			{
				"ps_key": "1122336553_41_20010_1",
				"sn": "VOPT001910205"
			}
		],
		"code": "1"
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
2.3 错误码
错误码
描述
1
正常
9
暂无权限



查询优化器的实时数据API
Post
/openapi/getMlpeRealTimeData

查询优化器的实时数据API
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_key_list
List
是
["700666130_22_247_3","700666130_22_247_2","700666130_14_1_2"]
优化器的ps_key列表，单次查询不超过100个
point_id_list
List
是
["83022","13134","13112","13176"]
需要查询的测点列表，现支持测点列表：58101,58103,58104,58105,58106,58107
{
	"ps_key_list": [
		"1122336553_41_10011_1",
		"1122336553_41_10012_1"
	],
	"point_id_list": [
		"p58101",
		"p58103"
	]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240827f14e40d88c0dd847063fdf6e
请求序列号
result_msg
String
success
提示信息
result_code
String
1
错误码
result_data
Map
--
返回数据
fail_ps_key_list
List
["700666130_22_247_3","700666130_22_247_2","700666130_14_1_2"]
失败的ps_key集合
result_data.device_point_list
List
--
每个设备测点值集合
result_data.device_point_list.device_point
String
--
测点集合
result_data.device_point_list.device_point.device_time
String
20240822195000
设备数据更新时间
result_data.device_point_list.device_point.ps_id
String
702966130
电站ID
result_data.device_point_list.device_point.ps_key
String
700926130_22_247_2
设备的ps_key
result_data.device_point_list.device_point.p+point_id
String
84300
测点对应值，如p1表示point_id=1的测点值
2.1 成功示例
{
	"req_serial_num": "20241128f42c46b19b3547d115a5b5fd",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"device_point_list": [{
				"device_point": {
					"p58101": "194.2",
					"ps_key": "700666130_22_247_3",
					"p58103": "19.2",
					"device_time": 20230116151500
				}
			},
			{
				"device_point": {
					"p58101": "59.7",
					"ps_key": "700666130_22_247_2",
					"p58103": "79.2",
					"device_time": 20230116151500
				}
			}
		]
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
3. 更多信息
3.1 优化器测点
设备类型	测点ID	测点名称	单位
优化器	58101	累计发电量	Wh
58103	输入电压	V
58104	输出电压	V
58105	输入电流	A
58106	输出电流	A
58107	输出功率	W
查询优化器的历史测点分钟级数据
Post
/openapi/getMlpeMinuteDataList

查询优化器的历史测点分钟级数据 取设备分钟数据，主要用于提供给第三方平台使用。注意：时间跨度不能超过3小时。注意：该接口返回的数据的单位都是最小单位，如发电量数据对应的单位都是最小单位wh，功率数据对应的单位都是最小单位w。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
points
String
是
p3022,p83024
测点id，多个测点使用逗号隔开；当前仅支持p58101,p58103,p58104,p58105,p58106,p58107
ps_key_list
String
是
["700665992_14_6_1","705286_1_1_1"]
优化器的ps_key，支持单次最多100个
start_time_stamp
String
是
20230103091800
开始时间格式：yyyyMMddHHmmss
end_time_stamp
String
是
20230103092300
结束时间格式：yyyyMMddHHmmss
minute_interval
String
是
15
分钟的时间间隔 如：15 代表每15分钟的测点数据 如果不传或者为空，则默认查询每5分钟的测点数据，必须为5的整数倍
{
	"minute_interval": "",
	"is_get_point_dict": "1",
	"points": "p13134,p13112,p13176,p13175",
	"start_time_stamp": "20240825091500",
	"end_time_stamp": "20240825231500",
	"ps_key_list": [
		"700666130_14_1_3",
		"700666130_14_1_2",
		"683399_1_1_1"
	]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
2024082955a04f67b07e156a973d54b1
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.{ps_key}
List
7006**992_14_6_1
设备的ps_key
result_data.{ps_key}.{p+point_id}
String
p13175
测点值（说明：该出参如：p1,p83022）
result_data.{ps_key}.time_stamp
String
20240825091500
时间（电站所在时区时间）
2.1 成功示例
{
	"req_serial_num": "2024082955a04f67b07e156a973d54b1",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"700665992_14_6_1": [{
				"p13175": "0.0",
				"time_stamp": "20240825091500",
				"p13176": "0.0",
				"p13134": "0.0",
				"p13112": "0.0"
			},
			{
				"p13175": "0.0",
				"time_stamp": "20240825092000",
				"p13176": "0.0",
				"p13134": "0.0",
				"p13112": "0.0"
			},
			{
				"p13175": "0.0",
				"time_stamp": "20240825092500",
				"p13176": "0.0",
				"p13134": "0.0",
				"p13112": "0.0"
			},
			{
				"p13175": "0.0",
				"time_stamp": "20240825093000",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
3. 更多信息
3.1 优化器测点
设备类型	测点ID	测点名称	单位
优化器	58101	累计发电量	Wh
58103	输入电压	V
58104	输出电压	V
58105	输入电流	A
58106	输出电流	A
58107	输出功率	W


查询优化器的的历史测点日月年数据
Post
/openapi/getMlpeDayMonthYearDataList

查询优化器的的历史测点日月年数据 根据开始时间和结束时间以及设备ps_key，和数据类型来获取设备的日月年数据相关数据，支持多测点查询。注意：该接口返回的数据的单位都是最小单位，如发电量数据对应的单位都是最小单位wh，功率数据对应的单位都是最小单位w。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
ps_key_list
List
是
["700009960_14_1_1","700009960_14_3_1"]
优化器的ps_key，支持单次最多100个
data_point
String
是
p13134,p13112,p13176,p13175
格式p+测点，多个测点使用逗号隔开。例如：如果查询的设备的ps_key是逆变器设备，则 p1表示逆变器发电量（返回数值对应单位为Wh），p2表示逆变器累计发电量（返回数值对应单位为Wh），p24表示逆变器总有功功率（返回数值对应单位为W），具体开放测点定义信息通过常用遥测测点获取。
start_time
String
是
20240823
开始时间 说明： query_type为day的时候，日期格式为yyyyMMdd, query_type为month的时候，日期格式为yyyyMM, query_type为year的时候，日期格式为yyyy
end_time
String
是
20240825
结束时间 说明： query_type为day的时候，日期格式为yyyyMMdd, query_type为month的时候，日期格式为yyyyMM, query_type为year的时候，日期格式为yyyy
data_type
String
是
1
1：均值，2：峰值，3：谷值，4：合计值（日维度的数据无合计值，月年维度的数据才有合计值） 多个使用逗号隔开。 如果是可以进行合计的数据，则： 查询日数据的时候，data_type为2， 查询月数据的时候，data_type为4， 查询年数据的时候，data_type为4
order
String
是
1
排序方式： 1 倒序， 0 正序（按照时间的顺序）
query_type
String
是
1
查询类型： 查询日数据：1 查询月数据：2 查询年数据：3
{
	"query_type": "1",
	"data_type": "2",
	"data_point": "p13134,p13112,p13176,p13175",
	"start_time": "20240823",
	"end_time": "20240825",
	"ps_key_list": ["700009960_14_1_1", "700009960_14_3_1"]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240827a1a74aecbdc4fe12f65055a6
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.{ps_key}
String
700009960_14_1_1
设备的ps_key
result_data.{ps_key}.{p+point_id}
String
[{"2": "371600.0000","time_stamp": "20240823"}
测点对应的数据集合
result_data.{ps_key}.{p+point_id}.{data_type}
String
371600.0000
对应的查询的data_type的数据（如：1），参照入参中的data_type参数
result_data.{ps_key}.{p+point_id}.time_stamp
String
20240823
对应的日期
2.1 成功示例
{
	"req_serial_num": "20240827a1a74aecbdc4fe12f65055a6",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"700009960_14_1_1": {
			"p13175": [{
					"2": "371600.0000",
					"time_stamp": "20240823"
				},
				{
					"2": "371600.0000",
					"time_stamp": "20240824"
				},
				{
					"2": "371600.0000",
					"time_stamp": "20240825"
				}
			],
			"p13176": [{
					"2": "1370784.8400",
					"time_stamp": "20240823"
				},
				{
					"2": "1414974.5200",
					"time_stamp": "20240824"
				},
				{
					"2": "1457428.2800",
					"time_stamp": "20240825"
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
3. 更多信息
3.1 优化器测点
设备类型	测点ID	测点名称	单位
优化器	58101	累计发电量	Wh
58103	输入电压	V
58104	输出电压	V
58105	输入电流	A
58106	输出电流	A
58107	输出功率	W



参数设置校验
Post
/openapi/paramSettingCheck

参数设置之前校验当前设备是否可以进行参数设置。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
set_type
Integer
是
2
参数设置类型： 0：参数设置， 2：参数回读
uuid
String
否
202**25197
设备的uuid，多设备使用英文逗号分隔传入。当set_type=2时，仅支持操作单个设备。
{
	"set_type":"2"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241126837f44e894ac5de13dca72fe
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.check_result
String
1
是否校验通过(指整体入参校验) ，0：校验不通过，1：校验通过，5：设备不存在，6：设备离线
result_data.dev_result_list
List
--
设备校验相关详情
result_data.dev_result_list.check_msg
String
success
检查结果
result_data.dev_result_list.check_result
String
1
是否校验通过(指单个设备校验) ，0：校验不通过，1：校验通过，5：设备不存在，6：设备离线
result_data.dev_result_list.uuid
String
2024***197
设备UUID
2.1 成功示例
{
    "req_serial_num": "202408273fc640e7a270484902d2822c",
    "result_code": "1",
    "result_msg": "success",
    "result_data": {
        "check_result": "1",
        "dev_result_list": [
            {
                "check_result": "5",
                "uuid": "2022377179"
            },
            {
                "check_result": "1",
                "check_msg": "success",
                "uuid": "3751206"
            }
        ]
    }
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
2.3 错误码
错误码
描述
0
校验不通过
1
校验通过
5
设备不存在
6
设备离线



参数设置任务下发
Post
/openapi/paramSetting

通过接口下发对应的设备的参数设置信息。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
expire_second
Integer
是
1800
参数设置任务的超时时间，单位为秒,数据范围为[0,1800]
param_list
List
是
--
设置的参数：每个元素的数据类型为Map，key为param_code和set_value, value为参数的测点id和参数设置的值
param_list.param_code
Integer
是
10641
参数代码，请参考控制参数代码定义
param_list.set_value
String
是
207
参数的设置值，如果是进行参数回读，该参数传空，否则该参数必传
set_type
String
是
2
参数设置类型： 0：参数设置， 2：参数回读， 默认0
task_name
String
是
2024-08-26 03:53:43 Remote Parameter Query
本次参数设置任务名称
uuid
String
是
2024525197
设备的uuid，多设备使用英文逗号分隔传入。当set_type=2时，仅支持操作单个设备。
{
    "set_type": 2,
    "uuid": "1820033",
    "task_name": "2024-09-11 16:55 逆变器远程参数查询",
    "expire_second": 1800,
    "param_list": [
		{
			"param_code": 10011,
			"set_value": ""
		}
	]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20241126cfb44e27a5ad5077f7252b88
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.check_result
String
1
错误编码（指整体错误校验），0:校验不通过无法进行参数设置，1:任务下发成功，2:参数设置测点重复，3:设置的参数个数超过上限，4:参数设置的测点id或设置值为空，5:设备不存在，6:参数设置模板未配置，7:设备离线，8:超时时间不在[0-1800]秒范围内，9:请勿重复操作，11:参数回读时，只允许单设备操作，12:存在设备当前版本不支持负值设置，请升级Logger1000或重新设置
result_data.dev_result_list
List
--
设备操作相关详情
result_data.dev_result_list.code
String
1
错误编码（指单个设备），0:校验不通过无法进行参数设置；1:任务下发成功；2:参数设置测点重复；3:设置的参数个数超过上限；4:参数设置的测点id或设置值为空；5:设备不存在；6:参数设置模板未配置；6-1: 设备机型不支持当前设置点或账号没有当前设置点的操作权限；7:设备离线；14：通信设备下行通道已关闭，请连接通信设备开启后操作
result_data.dev_result_list.msg
String
Operation Successful
信息
result_data.dev_result_list.task_id
String
100002733
参数设置任务id
result_data.dev_result_list.task_name
String
2024-08-24 17:51 Inverter Parameter Query
任务名称
result_data.dev_result_list.uuid
String
2024*25197
设备的uuid，多设备使用英文逗号分隔传入。当set_type=2时，仅支持操作单个设备。
result_data.not_support_negative_num_uuids
List
--
check_result=12 时返回不支持复制设置的设备 uuid
2.1 成功示例
{
	"req_serial_num": "202409117b5d4180977543b3255aa71a",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"check_result": "1",
		"dev_result_list": [
			{
				"msg": "操作成功",
				"task_name": "2024-09-11 16:55 逆变器远程参数查询",
				"code": "1",
				"task_id": "100002733",
				"uuid": "1820033"
			}
		]
	}
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
2.3 错误码
错误码
描述
0
校验不通过无法进行参数设置
1
任务下发成功
2
参数设置测点重复
3
设置的参数个数超过上限
4
参数设置的测点id或设置值为空
5
设备不存在
6
参数设置模板未配置
7
设备离线
8
超时时间不在[0-1800]秒范围内
9
请勿重复操作
11
参数回读时,只允许单设备操作



参数设置结果查询
Post
/openapi/getParamSettingTask

通过参数设置任务id查询参数设置结果信息。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
task_id
String
是
2289959
任务id
uuid
String
是
11809790
设备UUID
{
    "task_id": "100002733",
    "uuid": "1820033"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
2024112641cb43a388f799cdd8282280
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.command_status
Integer
2
任务状态：2:执行中，8:执行结束
result_data.create_time
String
2024-09-11 18:17:35
创建时间
result_data.create_time_zone
String
2024-09-11T18:17:35+08:00
用户时区的创建时间 格式:yyyy-MM-dd'T'HH:mm:ssXXX
result_data.over_time
String
2024-09-11 18:17:35
任务的完成时间，格式：yyyy-MM-dd HH:mm:ss
result_data.over_time_zone
String
2024-09-11T18:17:35+08:00
用户时区的任务的完成时间，格式:yyyy-MM-dd'T'HH:mm:ssXXX
result_data.param_list
List
--
任务对应的参数信息，说明：以下出参全部在param_list集合里面
result_data.param_list.command_status
Integer
4
该参数对应的指令状态： 1:等待执行，2:执行中，4:成功，5:失败， 6:超时
result_data.param_list.create_time
String
2024-09-11 18:17:35
创建时间
result_data.param_list.create_time_zone
String
2024-09-11T18:17:35+08:00
用户时区的创建时间 格式:yyyy-MM-dd'T'HH:mm:ssXXX
result_data.param_list.param_code
String
10011
参数代码，请参考控制参数代码定义
result_data.param_list.point_id
String
10641
测点ID
result_data.param_list.point_name
String
Daily Yield of Plant
测点名称
result_data.param_list.return_value
String
start
返回值（参数回读的时候表示参数回读值）
result_data.param_list.set_precision
String
1
参数的精度（具体请参考参数设置测点说明）
result_data.param_list.set_val_name
String
Total PV Feed-in Energy Adjustment
可以设置的值对应的名称
result_data.param_list.set_val_name_val
String
0
可以设置的值
result_data.param_list.set_value
String
1
设置值
result_data.param_list.unit
String
Wh
参数的单位（具体请参考参数设置测点说明）
result_data.param_list.update_time
String
2024-08-24 18:36:37
更新时间
result_data.param_list.update_time_zone
String
2024-08-16T12:00:00+00:00
用户时区的更新时间，格式:yyyy-MM-dd'T'HH:mm:ssXXX
result_data.task_id
Integer
100001604
任务id
result_data.task_name
String
2024-08-26 03:53:43 Remote Parameter Query
任务名称
2.1 成功示例
{
	"req_serial_num": "2024091183104a92ac0bf6b96e9bc15c",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"task_name": "2024-09-11 16:55 逆变器远程参数查询",
		"command_status": 2,
		"over_time_zone": null,
		"create_time": "2024-09-11 18:17:35",
		"task_id": 100002733,
		"create_time_zone": "2024-09-11T18:17:35+08:00",
		"over_time": null,
		"param_list": [
			{
				"command_status": 1,
				"point_id": "10641",
				"return_value": "",
				"set_value": "",
				"create_time": "2024-09-11 18:17:35",
				"param_code": "10011",
				"create_time_zone": "2024-09-11T18:17:35+08:00",
				"set_precision": "1",
				"point_name": "开/关机",
				"unit": "",
				"update_time": "2024-09-11 18:17:35",
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}

下发只读参数读取任务
Post
/openapi/readOnlyParamSet

下发只读参数读取任务
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
param_list
List
是
[10000]
需要获取的只读参数的编码
uuid_list
List
是
[1820033]
设备的uuid，当前只支持逆变器
{
  "param_list":[10000],
	"uuid_list":[1820033]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202409114866427ba6f71b475f4688ea
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
List
--
返回数据
result_data.code
String
1
错误编码（指单个设备）1：操作成功，2：设备不存在或离线，3：已下发不可再次下发，4：设备不支持该只读测点的获取，5：通信设备不支持只读参数的读取，14：通信设备下行通道已关闭，请连接通信设备开启后操作
result_data.uuid
String
1820033
设备的uuid，多设备使用英文逗号分隔传入。当set_type=2时，仅支持操作单个设备。
result_data.task_id
String
100002732
任务id
2.1 成功示例
{
	"req_serial_num": "202409114866427ba6f71b475f4688ea",
	"result_code": "1",
	"result_msg": "success",
	"result_data": [
		{
			"code": "1",
			"task_id": "100002732",
			"uuid": "1820033"
		}
	]
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}
2.3 错误码
错误码
描述
1
操作成功
2
设备不存在或离线
3
已下发不可再次下发
4
设备不支持该只读测点的获取
5
通信设备不支持只读参数的读取
14
通信设备下行通道已关闭，请连接通信设备开启后操作



只读参数读取结果查询
Post
/openapi/getReadOnlyResult

通过只读参数读取任务id查询任务执行结果。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
task_list
List
是
[100001766,100001762,100001761]
任务id集合
{
    "task_list": [100002736]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240911a4c7477aa6bb7cb53a038130
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
List
--
返回数据
result_data.task_detail_list
List
--
任务详细信息
result_data.task_detail_list.command_status
Integer
1
任务状态（1 等待执行，2 执行中，4 成功，5 失败，6 超时，9 取消）
result_data.task_detail_list.modbus_address
String
5633
Modbus地址
result_data.task_detail_list.param_code
Integer
10000
参数编码
result_data.task_detail_list.point_id
Integer
13141
测点信息
result_data.task_detail_list.return_value
String
1
只读的返回值
result_data.task_detail_list.unit
String
%
单位
result_data.task_id
String
100002736
任务id
result_data.uuid
Integer
1820033
设备的uuid，多设备使用英文逗号分隔传入。当set_type=2时，仅支持操作单个设备。
2.1 成功示例
{
	"req_serial_num": "20240911a4c7477aa6bb7cb53a038130",
	"result_code": "1",
	"result_msg": "success",
	"result_data": [
		{
			"code": "1",
			"task_detail_list": [
				{
					"command_status": 1,
					"point_id": "13141",
					"return_value": null,
					"unit": "%",
					"modbus_address": "5633",
					"ps_id": 196044,
					"task_id": 100002736,
					"param_code": 10000
				}
			],
			"task_id": "100002736",
			"uuid": "1820033"
		}
	]
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


查询只读参数定义
Post
/openapi/getReadOnlyParamDefinition

查询只读参数定义
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述

暂无数据
{
    "appkey":"D6488E8EE9A74B7E3F4144FAA4EC437A"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20240911bdc541c99768b97200e04e17
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
List
--
返回数据
result_data.param_code
Integer
10000
参数编码
result_data.param_name
String
Battery Level (SOC)
参数名称
2.1 成功示例
{
	"req_serial_num": "20240911bdc541c99768b97200e04e17",
	"result_code": "1",
	"result_msg": "success",
	"result_data": [
		{
			"param_code": 10000,
			"param_name": "电池电量"
		}
	]
}
2.2 失败示例
{
    "result_msg": "er_token_login_invalid",
    "result_data": null,
    "result_code": "E00003"
}


查询设备参数设置历史
Post
/openapi/getDeviceSettingRecordList

根据设备UUID和参数代码查询参数设置历史。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
paramList
List
是
[10011, 10008]
参数代码集合，请参考控制参数代码定义，数量上限100
uuidList
List
是
[2138342929, 2138297530]
设备uuid集合，数量上限100
taskIdList
List
否
[100080374, 100080380]
任务id集合，数量上限100
startTime
String
是
2025-07-17 00:00:00
开始时间，格式：yyyy-MM-dd HH:mm:ss。开始结束时间跨度不超过31天
endTime
String
是
2025-07-18 23:59:59
结束时间，格式：yyyy-MM-dd HH:mm:ss。开始结束时间跨度不超过31天
commandStatusList
List
否
[4]
任务状态, 1: 等待执行, 2: 执行中, 4: 成功, 5:失败, 6: 超时, 9: 取消。如果不传，则默认只查成功状态的历史记录。
{
	"paramList": [10011, 10008],
	"uuidList": [2138342929, 2138297530],
	"commandStatusList": [4],
	"taskIdList": [100080374, 100080380],
	"startTime": "2025-07-17 00:00:00",
	"endTime": "2025-07-18 23:59:59"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20250728209a46b896583dc18ebe66f4
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.data
List
--
每个设备测点记录集合
result_data.data.taskName
String
2025-07-28 10:10 Remote Parameter Query
任务名称
result_data.data.psId
Integer
7006**188
电站ID
result_data.data.deviceUuid
Integer
21383**929
设备UUID
result_data.data.setValue
String
207
设置值
result_data.data.returnValue
String
207
返回值（参数回读的时候表示参数回读值）
result_data.data.commandStatus
Integer
4
任务状态（1 等待执行，2 执行中，4 成功，5 失败，6 超时，9 取消）
result_data.data.remark
String
成功
备注
result_data.data.setPrecision
String
1
参数的精度（具体请参考参数设置测点说明）
result_data.data.unit
String
s
参数的单位（具体请参考参数设置测点说明）
result_data.data.isReadOnly
Integer
0
是否只读
result_data.data.taskSource
Integer
1
任务来源: 1=页面下发, 2=对外API
result_data.data.createTime
String
2025-07-28 10:10:56
任务详情创建时间，格式：yyyy-MM-dd HH:mm:ss
result_data.data.updateTime
String
2025-07-28 10:11:37
任务详情更新时间，格式：yyyy-MM-dd HH:mm:ss
result_data.data.userEnglishName
String
autotest1
用户名称
result_data.data.userName
String
cha dmin11
用户名称
result_data.data.paramCode
Integer
10011
参数代码，请参考控制参数代码定义
2.1 成功示例
{
	"req_serial_num": "20250728209a46b896583dc18ebe66f4",
	"result_code": "1",
	"result_msg": "success",
	"result_data": {
		"data": [{
				"taskName": "2025-07-28 10:10 Remote Parameter Query",
				"psId": 700688188,
				"deviceUuid": 2138342929,
				"setValue": "207",
				"returnValue": "207",
				"commandStatus": 4,
				"remark": "成功",
				"setPrecision": "1",
				"unit": null,
				"isReadOnly": 0,
				"taskSource": 1,
				"createTime": "2025-07-28 10:10:56",
				"updateTime": "2025-07-28 10:11:37",
				"userEnglishName": "",
				"userName": "cha dmin11",
				"paramCode": 10011
			},
			{
				"taskName": "2025-07-28 10:31 Remote Parameter Query",
2.2 失败示例
{
	"req_serial_num": "20250729cc714c6299606395f45ac096",
	"result_code": "010",
	"result_msg": "er_parameter_value_invalid:uuidList",
	"result_data": null
}

实时数据订阅功能使用说明
通常情况下，逆变器的测点数据是5分钟上报一次，在某些场景下，我们可能希望数据上报频率更快，实时数据订阅提供了控制逆变器上报测点数据的频率的功能。

1. 前提
（1）mqtt账号和密码申请

（2）逆变器支持实时数据订阅功能，请参考支持实时数据订阅的测点

2. 账号申请
实时数据功能需要您提交申请之后，我们为您分配mqtt用户名和密码，才能够进行调用。

2.1 申请流程
（1）准备申请材料

请详细说明您对开放API项目中特定功能的需求，包括但不限于您计划使用这些功能的业务场景、预期的使用频率等信息。
请提供您在开发者门户中申请API时使用的appkey或应用名称。
（2）发送申请材料至指定邮箱

请将您准备好的申请资料发送至 developer-api@sungrowpower.com。
在邮件主题中，请注明“开放API实时数据申请 - [您的姓名/企业名称]”，以便我们能够快速识别您的申请。
（3）等待审核与反馈

我们将在收到您的申请后的10个工作日内进行审核。审核过程中，如果我们需要您补充任何信息，我们会通过您提供的邮箱与您联系。
如果您的申请通过审核，我们会将分配给您的用户名和密码发送至您的申请邮箱。
2.2 注意事项
（1）请确保您提供的申请资料真实、准确、完整，这将有助于我们快速处理您的申请。

（2）在未收到我们分配的用户名和密码之前，请不要尝试调用需要申请权限的功能，以免造成不必要的错误。

（3）如果您在申请过程中有任何疑问或者遇到任何问题，可以通过邮箱与我们联系。

3. 使用步骤
3.1 根据appkey获取对应的mqtt信息
调用接口/openapi/datasubscribe/getConfig获取mqtt账号信息。如果您已经申请并分配mqtt账号，该接口会返回mqtt相关信息，包括：mqtt的连接地址、账号、密码、该appkey支持的mqtt协议类型、mqtt公钥。接口详情请参考接口文档：根据appkey获取对应的mqtt信息

3.2 开启实时数据上传功能
调用开启实时数据订阅接口/openapi/datasubscribe/start，给逆变器下发指令，开启实时数据上传功能。该接口会返回每个逆变器实时数据上报的topic，接口详情请参考接口文档：开启实时数据上传功能

3.3 关闭实时数据上传功能
调用接口/openapi/datasubscribe/stop，给逆变器下发指令，关闭实时数据上传。接口详情请参考接口文档：关闭实时数据上传功能

3.4 获取逆变器上报的实时数据
(1) 实时消费实时数据



使用mqtt连接工具，例如MQTTX，登录mqtt账号，连接到mqtt服务，并订阅第二步中接口返回的topic。mqtt连接时需要填入如下信息：

连接名称：可以输入任意字符
Client ID：需要保证全局唯一
Host：包括mqtt协议类型和mqtt主机。对应步骤1中接口返回的mqtt_url_list字段的协议类型和主机部分
Port：mqtt服务端口号。对应步骤1中接口返回的mqtt_url_list的端口号部分
Path：mqtt访问路径，只要当使用的mqtt协议是ws或者wss时才需要，默认为/mqtt。对应步骤1中接口返回的mqtt_url_list的路径部分
Username：mqtt账号，对应步骤1中接口返回的mqtt_username字段
Password：mqtt密码，对应步骤1中接口返回的mqtt_password字段


注意事项：

mqtt消费到的原始报文是加密的，可以通过第一步中获取到的RSA公钥解密数据。mqtt_rsa_public_key解密数据。
如果不需要实时的查看设备上报的数据，可以不进行该操作和第一步。
使用RSA公钥解密代码示例：


import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.IOUtils;

import javax.crypto.Cipher;
import java.io.ByteArrayOutputStream;
import java.security.KeyFactory;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.X509EncodedKeySpec;

/**
 * RSA公钥解密
 **/
public static String publicDecrypt(String data, String publicKey){
    String result = null;
    try{
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(Base64.decodeBase64(publicKey));
        RSAPublicKey key = (RSAPublicKey) keyFactory.generatePublic(x509KeySpec);
        Cipher cipher = Cipher.getInstance("RSA");
        cipher.init(Cipher.DECRYPT_MODE, key);
        result = new String(rsaSplitCodec(cipher, Cipher.DECRYPT_MODE, Base64.decodeBase64(data), key.getModulus().bitLength()), "UTF-8");
    }catch(Exception e){
        //Deal Exception
    }
    return result;
}

private static byte[] rsaSplitCodec(Cipher cipher, int opmode, byte[] datas, int keySize){
    int maxBlock;
    if(opmode == Cipher.DECRYPT_MODE){
        maxBlock = keySize / 8;
    }else{
        maxBlock = keySize / 8 - 11;
    }
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    int offSet = 0;
    byte[] buff;
    int i = 0;
    byte[] resultDatas = null ;
    try{
        while(datas.length > offSet){
            if(datas.length-offSet > maxBlock){
                buff = cipher.doFinal(datas, offSet, maxBlock);
            }else{
                buff = cipher.doFinal(datas, offSet, datas.length-offSet);
            }
            out.write(buff, 0, buff.length);
            i++;
            offSet = i * maxBlock;
        }
        resultDatas = out.toByteArray();
    } catch(Exception e){
        //Deal Exception
    } finally {
        IOUtils.closeQuietly(out);
    }
    return resultDatas;
}
(2) 查询历史数据

调用获取历史数据接口/openapi/datasubscribe/getHisData查询设备上报的历史数据。接口详情请参考接口文档：获取历史数据



根据appkey获取对应的Mqtt信息
Post
/openapi/datasubscribe/getConfig

该接口根据入参中的appkey获取该appkey对应的Mqtt公钥、Mqtt地址、用户名和密码等信息。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
appkey
String
是
ABB4C02A3C9F5A95EF0A9A1BF4DAFF3A
应用的AppKey
{
    "appkey": "ABB4C02A3C9F5A95EF0A9A1BF4DAFF3A",
    "sys_code": 200
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20250106999d460297ea0f24268219e0
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.mqtt_type
String
3
该appkey支持的mqtt协议类型：1：tcp 2：ws 3：ws和tcp
result_data.mqtt_url_list
List
--
Mqtt连接地址(当前appey支持的连接地址集合)
result_data.mqtt_username
String
sungrow
Mqtt用户名
result_data.mqtt_password
String
123456
Mqtt密码
result_data.mqtt_rsa_public_key
String
MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKQHhDVKSi8OsxRKXfH4/e/3YCeHF1UshpN/38ieCBflLzbC3AWkBE3Ury7tYyNmHbpPZSOW235oCaapzHZRcCAwEAAQ==
Mqtt公钥
result_data.code
String
1
操作编码：1：成功获取；0：获取失败；2：该appkey不支持Mqtt消息订阅；
2.1 成功示例
{
	"req_serial_num":"20250106999d460297ea0f24268219e0",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"mqtt_type":"3",
		"mqtt_url_list":[
			"tcp://testiot.isolarcloud.com:9999",
			"ssl://secure-testiot.isolarcloud.com:9997"
		],
		"mqtt_username":"sungrow",
		"mqtt_password":"123456",
		"mqtt_rsa_public_key":"MFwwDQYJKoZIhvcNAQEBBQADSwAwSBAKQHhDVKVKSi8OsxRKXfH4/e/3YCeHF1UshpN/38ieCBflLzbC3AWkBE3Ury7tYyNmHbpPZSOWYo5oCaapzHZRcCAwEAAQ==",
		"code":"1"
	}
}
2.2 失败示例
{
	"result_msg":"er_invalid_appkey",
	"result_data":null,
	"result_code":"E00000"
}


开启实时数据上传功能
Post
/openapi/datasubscribe/start

给逆变器下发指令，开启实时数据上传功能 ,可通过mqtt订阅实时数据。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
second
Integer
是
--
上传频率（单位秒），默认60s，不能小于5s，如：10就是10s上传一次
sn_list
List
是
--
设备（逆变器）sn，最多10个
{
    "second": 60,
    "sn_list": ["A2351607928","A2360216235"]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202205072ace4107a936e2167af8e4cf
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.success_list
List
--
成功的sn列表
result_data.success_list.sn
String
A10*****00
逆变器S/N
result_data.success_list.topic
String
sungrow_data_monitor_info
mqtt的topic
result_data.fail_list
List
--
失败的sn列表
result_data.fail_list.code
Integer
0
错误码：0：该设备不为逆变器或不存在，1：该设备不属于用户，2：设备不支持实时数据功能，3：该设备不在线，14：通信设备下行通道已关闭，请连接通信设备开启后操作
result_data.fail_list.sn
String
A10*****00
设备S/N
2.1 成功示例
{
    "req_serial_num": "202205072ace4107a936e2167af8e4cf",
    "result_code": "1",
    "result_data": {
        "success_list":[{
            "sn":"A10*****00",
            "topic":"sungrow_data_monitor_info"
        },
        {
            "sn":"A10***2",
            "topic":"sungrow_data_monitor_info"
        }],
        "fail_list":[{
            "sn":"A1000003",
            "code":0
        }]
    },
    "result_msg": "success"
}
2.2 失败示例
{
    "error": "invalid_token",
    "error_description": "Invalid access token",
    "req_serial_num": "202408265afa4caa9e21089c9674390f"
}
2.3 错误码
错误码
描述
0
该设备不为逆变器或不存在
1
该设备不属于用户
2
设备不支持实时数据功能
3
该设备不在线
14
通信设备下行通道已关闭，请连接通信设备开启后操作
3. 更多信息
3.1 支持实时数据订阅功能的测点
测点ID	测点名称
13126	电池充电功率
13150	电池放电功率
13139	电池电流
13138	电池电压
13142	电池健康度
13141	电池电量
13007	电网频率
13008	A相电流
13157	A相电压
13149	电网取电功率
13011	有功功率
13012	总无功功率
13003	总直流功率
13121	馈网功率
13034	累计电池充电
13176	累计PV电池充电
13035	累计电池放电
13134	总PV发电量
13125	总馈网电量
13148	总电网取电电量
13137	总直接消耗电量
13175	累计PV馈网
13119	负载功率
13013	总功率因数


关闭实时数据上传功能
Post
/openapi/datasubscribe/stop

给逆变器下发指令，关闭实时数据上传功能
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
sn_list
List
是
--
设备sn列表，最多10个
{
    "sn_list": ["A2351607928","A2360216235"]
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
202205072ace4107a936e2167af8e4cf
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.success_list
List
--
成功的sn列表
result_data.success_list.sn
String
A20469XXX7
设备S/N
result_data.fail_list
List
--
失败的sn列表
result_data.fail_list.sn
String
A20469XXX7
设备S/N
result_data.fail_list.code
Integer
0
错误码：0：该设备不为逆变器或不存在，1：该设备不属于用户，2：设备不支持实时数据功能，3：该设备不在线，14：通信设备下行通道已关闭，请连接通信设备开启后操作
2.1 成功示例
{
    "req_serial_num": "202205072ace4107a936e2167af8e4cf",
    "result_code": "1",
    "result_data": {
        "success_list":[{
            "sn":"A10*****00"
        },
        {
            "sn":"A10***2"
        }],
        "fail_list":[{
            "sn":"A1000003",
            "code":0
        }]
    },
    "result_msg": "success"
}
2.2 失败示例
{
	"result_msg":"er_invalid_appkey",
	"result_data":null,
	"result_code":"E00000"
}
2.3 错误码
错误码
描述
0
该设备不为逆变器或不存在
1
该设备不属于用户
2
设备不支持实时数据功能
3
该设备不在线
14
通信设备下行通道已关闭，请连接通信设备开启后操作


获取历史数据
Post
/openapi/datasubscribe/getHisData

获取设备历史数据，目前我们仅提供最近一小时的数据。只有启用了实时数据上传功能的设备支持历史数据查询。
1. 请求参数
请求参数
参数类型
是否必传
参数示例
参数描述
sn_list
List
是
["111111111155"]
设备sn列表，最多10个
start_time
String
是
2025-01-06T15:20:00+08:00
开始时间 （带时区），格式:yyyy-MM-dd'T'HH:mm:ssXXX
end_time
String
是
2025-01-06T16:20:00+08:00
结束时间 （带时区），格式:yyyy-MM-dd'T'HH:mm:ssXXX
{
    "appkey": "ABB4C02A3C9F5A95EF0A9A1BF4DAFF3A",
    "sys_code": 200,
    "sn_list": ["111111111155"],
    "start_time": "2025-01-04T15:37:19+11:00",
    "end_time": "2025-01-04T15:40:24+11:00"
}
2. 返回参数
返回参数
数据类型
示例值
描述
req_serial_num
String
20250106f8324c50bd27ed197df8adda
请求序列号
result_code
String
1
错误码
result_msg
String
success
提示信息
result_data
Map
--
返回数据
result_data.fail_list
List
--
失败的sn列表
result_data.fail_list.sn
String
A10*****00
设备SN
result_data.fail_list.code
Integer
1
错误码：0：该设备不为逆变器或不存在，1：该设备不属于用户，2：设备不支持实时数据功能，3：该设备不在线
result_data.success_list
List
--
成功的sn列表
result_data.success_list.dataList
List
--
测点数据
result_data.success_list.dataList.msgTime
String
2025-01-04T15:37:19+11:00
数据真实时间 （带时区），格式:yyyy-MM-dd'T'HH:mm:ssXXX
result_data.success_list.dataList.recvTime
String
2025-01-04T15:40:24+11:00
数据接收时间 （带时区），格式:yyyy-MM-dd'T'HH:mm:ssXXX
result_data.success_list.dataList.data
Map
--
测点数据
result_data.success_list.dataList.data.id
String
13150
测点
result_data.success_list.dataList.data.val
String
1173
测点值
result_data.success_list.sn
String
A10*****00
设备SN
2.1 成功示例
{
	"req_serial_num":"202501064b5e470eb265ee9e0c2fb658",
	"result_code":"1",
	"result_msg":"success",
	"result_data":{
		"fail_list":[],
		"success_list":[
			{
				"dataList":[
					{
						"msgTime":"2025-01-06T20:00:39+08:00",
						"recvTime":"2025-01-06T20:00:40+08:00",
						"data":[
							{
								"id":"13150",
								"val":"1173"
							},
							{
								"id":"13011",
								"val":"1173"
							},
							{
								"id":"13176",
								"val":"138500"
							},
							{
								"id":"13121",
								"val":"0"
							},
							{
								"id":"13034",
2.2 失败示例
{
	"result_msg":"er_invalid_appkey",
	"result_data":null,
	"result_code":"E00000"
}





附录1：设备类型字典定义
device_type	设备类型名称	设备类型英文名称
1	逆变器	Inverter
2	集装箱	Container
3	并网点	Grid-connection Point
4	汇流箱	Combiner Box
5	环境监测仪	Meteo Station
6	变压器	Transformer
7	电表	Meter
8	UPS	UPS
9	数据采集器	Data Logger
10	组串	String
11	电站	Plant
12	线路保护	Circuit Protection
13	解列装置	Splitting Device
14	储能逆变器	Energy Storage System
15	采集设备	Sampling Device
16	EMU	EMU
17	单元	Unit
18	温湿度传感器	Temperature and Humidity Sensor
19	智能配电柜	Intelligent Power Distribution Cabinet
20	显示设备	Display Device
21	交流配电柜	AC Power Distributed Cabinet
22	通信模块	Communication Module
23	系统BMS	System-BMS
24	阵列BMS	Array-BMS
25	直流-直流	DC-DC
26	能量管理系统	Energy Management System
27	跟踪系统	Tracking System
28	风能变流器	Wind Energy Converter
29	SVG	SVG
30	PT柜	PT Cabinet
31	母线保护	Bus Protection
32	清扫机器人	Cleaning Device
33	直流屏	Direct Current Cabinet
34	公用测控	Public Measurement and Control
37	储能变流器	Energiespeichersystem
41	优化器	Optimizer
43	电池	Battery
44	电池簇管理单元	Battery Cluster Management Unit
45	本地控制器	Local Controller
51	充电桩	Charger
52	电池系统控制器	Battery System Controller
55	微型逆变器	Microinverter
63	柴油发电机	Diesel Generator


附录2：API错误码定义
错误码名称	类型	错误代码
success	调用成功	1
error	服务内部异常	-1
er_unknown_exception	未知异常	000
er_missing_parameter:appkey	参数appkey不可以为空	001
er_missing_parameter:token	参数token不可以为空	002
er_missing_parameter:sys_code	参数sys_code不可以为空	003
er_invalid_appkey	appkey不合法	E00000
er_api_service_has_expired	API服务到期了	E00001
er_parameter_decrypt_error	参数解密异常	E00002
er_token_login_invalid	token不合法或已失效	E00003
er_month_call_api_times_upper_limit	API调用次数达上限	E998
er_hour_call_api_times_upper_limit	API调用次数达上限	E999
er_missing_parameter	必传参数缺失	009
er_parameter_value_invalid	参数值不合法	010
er_sql_exception	SQL异常	011
Unauthorized access	未经授权的访问	E900
Call too frequently	调用频繁	E901
Abnormal network environment	ip地址频繁切换	E903
Request is not encrypted	请求未加密	E902
Missing parameter in request header: x-random-secret-key	请求头缺失参数：x-random-secret-key	E904
AES decryption exception	AES解密异常	E905
RSA decryption exception	RSA解密异常	E906
AES random secret key length must be 16	AES随机秘钥长度必须为16	E907
Missing key parameter: api_key_param	缺失关键参数：api_key_param	E908
Invalid parameter format: nonce [32-bit string of numbers and letters]	参数格式不合法：nonce [数字和字母组合的32位字符串]	E909
Repeated request	重复的请求，请求中的nonce需要重新生成	E910
Missing parameter in request header: x-access-key	请求头缺失参数：x-access-key	E911
Illegal x-access-key	非法的 x-access-key	E912
Expired request	请求过期，请求中timestamp（0时区UNIX时间戳）与服务器时间差不在合理范围内	E913
Mismatched appkey and x-access-key	appkey与access-key不匹配	E914
Login too frequently	登录频繁	E916



附录3：明文调用API代码样例
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
public class UserTest{
    Public static void main(String[] args)
    {
        CloseableHttpClienthttpclient = HttpClients.createDefault();
        String url = "https://此处为阳光电源提供的API域名/xxx/xxx";
        HttpPosthttppost = new HttpPost(url);
        try
        {
            // 设置头
            httppost.addHeader("sys_code", "901");
            HashMap<String, Object>req = new HashMap<String, Object>();
            // 公共参数
            req.put("appkey", "授权的appkey");
req.put("token", "登录接口返回的token");
            // 业务相关
            req.put("service", "服务名称");
            req.put("参数名1", "参数值");
            String jsonStr = com.alibaba.fastjson.JSON.toJSONString(req);
            System.out.println("send json-<" + jsonStr.toString());
            StringEntitystrEntity = new StringEntity(jsonStr);
            strEntity.setContentType("application/json");
            httppost.setEntity(strEntity);
            CloseableHttpResponse response = httpclient.execute(httppost);
            try
            {
                HttpEntity entity = response.getEntity();
                InputStreaminputStream = entity.getContent();
                InputStreamReaderinputStreamReader = new InputStreamReader(
                        inputStream, "UTF-8");
                BufferedReader reader = new BufferedReader(inputStreamReader);
                StringBuilder result = new StringBuilder();
                String s;
                while (((s = reader.readLine()) != null))
                {
                    result.append(s);
                }
                reader.close();
                System.out.println("receive json-<" + result.toString());
            }
            finally
            {
                response.close();
            }
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        finally
        {
            try
            {
                httpclient.close();
            }
            catch (IOException e)
            {
                e.printStackTrace();
            }
        }
    }
}


附录4：RSA加密代码样例
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.IOUtils;
/**
* RSA加密规则：
*密钥格式：PKCS#8
*输出格式：Base64
*字符集：utf8编码；
**/
public String publicEncrypt(String data, String publicKey) {
    try {
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(Base64.decodeBase64(publicKey));
        RSAPublicKey key = (RSAPublicKey)keyFactory.generatePublic(x509KeySpec);
        Cipher cipher = Cipher.getInstance("RSA");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        return Base64.encodeBase64URLSafeString(rsaSplitCodec(cipher, Cipher.ENCRYPT_MODE,
        data.getBytes("UTF-8"), key.getModulus().bitLength()));
    } catch (Exception var3) {
        //Deal Exception
    }
}

private byte[] rsaSplitCodec(Cipher cipher, int opmode, byte[] datas, int keySize){
    int maxBlock = 0;
    if(opmode == Cipher.DECRYPT_MODE){
        maxBlock = keySize / 8;
    }else{
        maxBlock = keySize / 8 - 11;
    }
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    int offSet = 0;
    byte[] buff;
    int i = 0;
    try{
        while(datas.length > offSet){
            if(datas.length-offSet > maxBlock){
                buff = cipher.doFinal(datas, offSet, maxBlock);
            }else{
                buff = cipher.doFinal(datas, offSet, datas.length-offSet);
            }
            out.write(buff, 0, buff.length);
            i++;
            offSet = i * maxBlock;
        }
    }catch(Exception e){
        //Deal Exception
    }
    byte[] resultDatas = out.toByteArray();
    IOUtils.closeQuietly(out);
    return resultDatas;
}


附录5：AES加密代码样例
/**
*AES加密规则：
*加密模式：ECB
*填充方式：pkcs5padding
*数据块：128位
*偏移量：无偏移量
*输出：hex
*字符集：utf8编码
**/
public String encrypt(String content, String password)  throws Exception {
    try {
        byte[] result = null;
        byte[] passwordBytes = getSecretKey(password) ;
        SecretKeySpec skeySpec = new SecretKeySpec(passwordBytes, "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, skeySpec);
        result = cipher.doFinal(content.getBytes("UTF-8"));
        return parseByte2HexStr(result) ;
    } catch (Exception e) {
        //Deal Exception
    }
}

public byte[] getSecretKey(String key) throws Exception{
    final byte paddingChar = '0';
    byte[] realKey = new byte[16];
    byte[] byteKey = key.getBytes("UTF-8");
    for (int i =0;i<realKey.length;i++){
        if (i<byteKey.length){
            realKey[i] = byteKey[i];
        }else{
            realKey[i] = paddingChar;
        }
    }
    return realKey;
}

public String parseByte2HexStr(byte buf[]) {
    StringBuffer sb = new StringBuffer();
    for (int i = 0; i < buf.length; i++) {
        String hex = Integer.toHexString(buf[i] & 0xFF);
        if (hex.length() == 1) {
            hex = '0' + hex;
        }
        sb.append(hex.toUpperCase());
    }
    return sb.toString();
}


附录6：AES解密代码样例
/**
*解密模式：ECB
*填充方式：pkcs5padding
*数据块：128位
*偏移量：无偏移量
*输出：hex
*字符集：utf8编码；
**/

public  String decrypt(String content, String password) throws Exception {
    try {
        byte[] original = null;
        byte[] decryptFrom = parseHexStr2Byte(content);
        byte[] passwordBytes = getSecretKey(password) ;
        SecretKeySpec skeySpec = new SecretKeySpec(passwordBytes, "AES");
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE, skeySpec);
        original = cipher.doFinal(decryptFrom);
        return new String(original);
    } catch (Exception e) {
        //Deal Exception
    }
}

public byte[] parseHexStr2Byte(String hexStr) {
    if (hexStr.length() < 1) {
        return null;
    }
    byte[] result = new byte[hexStr.length() / 2];
    for (int i = 0; i < hexStr.length() / 2; i++) {
        int high = Integer.parseInt(hexStr.substring(i * 2, i * 2 + 1), 16);
        int low = Integer.parseInt(hexStr.substring(i * 2 + 1, i * 2 + 2),
                16);
        result[i] = (byte) (high * 16 + low);
    }
    return result;
}
附录6：AES解密代码样例


附录7：加密调用API代码样例
1.请求头封装
String publicKey = "xxxxx" ;// 阳光云分配的publicKey
// publicEncrypt 方法参考附录 3
String x-random-secret-key = publicEncrypt("A123456zA123456z", publicKey) ;//每次请求里x-random-secret-key可以不同
String x-access-key = "i71w7tskmns5********i3b8zqncvay3" ;//阳光云分配的accessKey

2.请求体封装
//以登录接口为例，除3.1章节请求体的参数之外，还需要增加api_key_param对象：
//nonce是32位长度的数字与字母的随机组合字符串.每次请求都不能与之前的重复；
//timestamp 是毫秒级的UNIX时间戳，如果调用返回错误码E913,
//则需要通过GET方式调用https://此处为阳光电源提供的API域名/timestamp接口进行时间校准
String requestBody =
{
    "api_key_param": {
        "nonce": "cb360459bd624c6ab15308c4b6847856",
        "timestamp": "1616725497384"
    },
    "appkey": "***********",
    "login_type": "1",
    "user_account": "******",
    "user_password": "******"
};

3.请求调用
CloseableHttpClient httpclient = HttpClients.createDefault();
String url = "https://此处为阳光电源提供的API域名/openapi/login";
HttpPost httppost = new HttpPost(url);
// 设置请求头
httppost.addHeader("x-random-secret-key", x-random-secret-key);
httppost.addHeader("x-access-key", x-access-key);
...... //设置其他请求头
// encrypt方法参考附录 4
String encryptedRequestBody = encrypt(requestBody, "A123456zA123456z") ;
StringEntity strEntity = new StringEntity(encryptedRequestBody);
strEntity.setContentType("application/json");
httppost.setEntity(strEntity);
CloseableHttpResponse response = httpclient.execute(httppost);
HttpEntity entity = response.getEntity();
InputStream inputStream = entity.getContent();
InputStreamReader inputStreamReader = new InputStreamReader(inputStream, "UTF-8");
BufferedReader reader = new BufferedReader(inputStreamReader);
StringBuilder responseBody = new StringBuilder();
String s = null;
while (((s = reader.readLine()) != null))
{
    responseBody.append(s);
}
reader.close();
// decrypt方法参考附录 5
String decryptedResponseBody = decrypt(responseBody, "A123456zA123456z") ;



附录8：故障码枚举
故障码	故障ID	设备型号	故障名
60001	1	逆变器	电网过压
60002	2	逆变器	电网欠压
60003	3	逆变器	电网过频
60004	4	逆变器	电网欠频
60005	5	逆变器	电网掉电
60006	6	逆变器	漏电流超标
60007	7	逆变器	电网异常
60008	8	逆变器	电网电压不平衡
60009	9	逆变器	PV反接故障
60010	10	逆变器	PV反接告警
60011	11	逆变器	PV异常告警
60012	12	逆变器	环境温度过高
60013	13	逆变器	环境温度过低
60014	14	逆变器	系统绝缘阻抗低
60015	15	逆变器	地线故障
60016	16	逆变器	AFCI故障
60017	17	逆变器	离网负载过功率故障
60018	18	逆变器	电表反接
60019	19	逆变器	电表通讯异常告警
60020	20	逆变器	电网冲突
60021	21	逆变器	并联通讯告警
60022	22	逆变器	BMS通信故障
60023	23	逆变器	电池接入异常
60024	24	逆变器	电池告警
60025	25	逆变器	电池故障
60026	26	逆变器	PV过压故障
60027	27	逆变器	MPPT反接
60028	28	逆变器	升压电容过压告警
60029	29	逆变器	升压电容过压故障
60030	30	逆变器	组串电流反灌
60032	32	逆变器	关断器异常告警
60035	35	逆变器	PV接地故障
60063	63	逆变器	系统告警
60064	64	逆变器	系统故障
13801	1	储能逆变器	电网过压
13802	2	储能逆变器	电网欠压
13803	3	储能逆变器	电网过频
13804	4	储能逆变器	电网欠频
13805	5	储能逆变器	电网掉电
13806	6	储能逆变器	漏电流超标
13807	7	储能逆变器	电网异常
13808	8	储能逆变器	电网电压不平衡
13809	9	储能逆变器	PV反接故障
13810	10	储能逆变器	PV反接告警
13811	11	储能逆变器	PV异常告警
13812	12	储能逆变器	环境温度过高
13813	13	储能逆变器	环境温度过低
13814	14	储能逆变器	系统绝缘阻抗低
13815	15	储能逆变器	地线故障
13816	16	储能逆变器	AFCI故障
13817	17	储能逆变器	离网负载过功率故障
13818	18	储能逆变器	电表反接
13819	19	储能逆变器	电表通讯异常告警
13820	20	储能逆变器	电网冲突
13821	21	储能逆变器	并联通讯告警
13822	22	储能逆变器	BMS通信故障
13823	23	储能逆变器	电池接入异常
13824	24	储能逆变器	电池告警
13825	25	储能逆变器	电池故障
13826	26	储能逆变器	PV过压故障
13827	27	储能逆变器	MPPT反接
13828	28	储能逆变器	升压电容过压告警
13829	29	储能逆变器	升压电容过压故障
13830	30	储能逆变器	组串电流反灌
13832	32	储能逆变器	关断器异常告警
13835	35	储能逆变器	PV接地故障
13863	63	储能逆变器	系统告警
13864	64	储能逆变器	系统故障
13893	517	储能逆变器	旁路开关过压
13894	518	储能逆变器	旁路开关欠压
13895	516	储能逆变器	旁路开关过流
13896	114	储能逆变器	旁路开关过流



附录9：控制参数代码定义
param_code	设备类型	参数名称	设置值或范围说明
10001	储能逆变器	SOC 上限	设置值范围为700-1000，表示70%~100%
10002	储能逆变器	SOC 下限	设置值范围为0-500，表示0%~50%
10003	储能逆变器	能量管理模式	0：自发自用模式，2：强制模式，3：外部能量调度，4：VPP调度默认0
10004	储能逆变器	充放电命令	170：充电，187：放电，204：停止默认204
10005	储能逆变器	充放电功率	设置值范围0~5000W，默认1000
10006	储能逆变器&光伏逆变器	改造系统使能	170：使能，85：关闭
10007	储能逆变器&光伏逆变器	限功率开关	170：使能，85：关闭
10008	储能逆变器&光伏逆变器	限功率百分比	设置值范围为0-1000，表示0~100%
10009	储能逆变器光伏逆变器	无功调节模式	85，关闭- OFF，161：功率因数设置启用-PF，162：无功比例设置启用-Q(t)，164：Q(U)线设置启用- Q(U)，163: Q(P)曲线设詈启用- Q(P)
10010	储能逆变器&光伏逆变器	无功比例	设置值范围为-600-600，表示-60%~60%
10011	储能逆变器&光伏逆变器	开机/关机	207：开机 206：关机 174：重启
10012	储能逆变器&光伏逆变器	馈网功率限制	170：使能，85：关闭
10012	Logger1000& EyeM4	馈网功率限制	1：使能，0：关闭
10013	储能逆变器&光伏逆变器	馈网功率限制值	设置值范围0~逆变器额定功率（设置该值的时候馈网功率限制要求必须设置）
10014	储能逆变器&光伏逆变器	馈网功率限制比例	设置值范围为0-1000，表示0~100%（设置该值的时候馈网功率限制要求必须设置）
10014	Logger1000& EyeM4	馈网功率限制比例	设置值范围-1000-1000，表示-100%~100%（设置该值的时候网功率限制要求必须设置）
注：Logger1000的数据采集器模式下控制测点
10015	储能逆变器	强制充电目标SOC1	设置值范围为：0-100，表示0~100%
10016	储能逆变器	强制充电目标SOC2	设置值范围为：0-100，表示0~100%
10017	储能逆变器	外部EMS心跳	设置值范围为：1-1000，表示1s~1000s
10024	储能逆变器	电池优先使能	170：使能，85：关闭
10025	储能逆变器&光伏逆变器	故障后有功缓启	170：使能，85：关闭
10026	储能逆变器&光伏逆变器	故障后有功缓启时间	故障后有功缓启使能后设置，范围为1-1200，表示1s~1200s
10027	储能逆变器&光伏逆变器	有功功率缓启	170：使能，85：关闭
10028	储能逆变器&光伏逆变器	有功功率缓启斜率	有功功率缓启使能后设置，范围5-10000，表示0.05%~100%
10029	储能逆变器&光伏逆变器	有功速度控制	170：使能，85：关闭
10030	储能逆变器&光伏逆变器	有功下降速度	有功速度控制使能后设置，范围为1-6000，表示1%/min~6000%/min
10031	储能逆变器&光伏逆变器	有功上升速度	有功速度控制使能后设置，范围为1-6000，表示1%/min~6000%/min
10032	储能逆变器&光伏逆变器	有功设置保持	170：使能，85：关闭
10033	储能逆变器&光伏逆变器	限功率0%关机	170：使能，85：关闭
10034	储能逆变器&光伏逆变器	无功响应	170：使能，85：关闭，只有在无功调节模式为PF，Qt，Q(P)，Q(U)时设置
10035	储能逆变器&光伏逆变器	无功响应时间	只有在无功调节模式为PF，Qt，Q(P)，Q(U)时设置，范围为1-6000，表示0.1s~600s
10036	储能逆变器&光伏逆变器	功率因数设置	只有在无功调节模式为PF时设置，范围为-1000-1000，表示-1~1
10065	储能逆变器&光伏逆变器	强制充电	85为禁止，170为使能
10066	储能逆变器&光伏逆变器	强制充电有效时间	0为工作日，1为每天
10067	储能逆变器&光伏逆变器	强制充电起始时间1:时	0~24（分钟必须为0），默认24
10068	储能逆变器&光伏逆变器	强制充电起始时间1:分	0~59，默认0
10069	储能逆变器&光伏逆变器	强制充电结束时间1:时	0~24（分钟必须为0），默认24
10070	储能逆变器&光伏逆变器	强制充电结束时间1:分	0~59，默认0
10071	储能逆变器&光伏逆变器	强制充电目标SOC1	数据下限为0，数据上限为100，单位为%
10072	储能逆变器&光伏逆变器	强制充电起始时间2:时	0~24（分钟必须为0），默认24
10073	储能逆变器&光伏逆变器	强制充电起始时间2:分	0~59，默认0
10074	储能逆变器&光伏逆变器	强制充电结束时间2:时	0~24（分钟必须为0），默认24
10075	储能逆变器&光伏逆变器	强制充电结束时间2:分	0~59，默认0
10076	储能逆变器&光伏逆变器	强制充电目标SOC2	数据下限为0，数据上限为100，单位为%
10082	Logger1000&能量管理系统	外部调度模式充放电命令	170：充电；187：放电；204：禁止
10083	Logger1000&能量管理系统	外部调度模式充放电功率	数据范围：0~电站级充放电上限范围描述, 可通过接口getDevPropertyPointValue 传入测点id:29046 查询具体范围数据
10085	Logger1000&能量管理系统	外部调度模式EMS心跳设置	数据范围：10~1000
10086	Logger1000&能量管理系统	能量管理模式	1：自发自用；2：时间计划；4：VPP调度；5: 强制模式
10087	Logger1000&能量管理系统	外部调度模式馈网功率限制比例	数据范围：-1000~1000，默认1000
注：Logger1000的能量管理模式下控制测点
10088	Logger1000&能量管理系统	外部调度模式馈网功率限制开关	数据范围：85：关 170： 开 默认值：关
10089	Logger1000&能量管理系统	外部调度模式馈网功率限制值	数采为-99999999~99999999 默认为0
10090	Logger1000&能量管理系统	PV限功率开关	枚举值0和1，1: 开启，0: 关闭
10091	储能逆变器	最大充电功率	数据范围：10~(最大充电功率上限范围描述*100)，可通过接口getDevPropertyPointValue 传入测点id:18290 查询“最大充电功率上限范围描述”，若无数据则范围默认为10~1060
10092	储能逆变器	最大放电功率	数据范围：10~(最大放电功率上限范围描述*100),，可通过接口getDevPropertyPointValue 传入测点id:18291 查询“最大放电功率上限范围描述”，若无数据则范围默认为10~1060
10095	能量管理系统	功能投退	1：Enable，0：Disable
10096	能量管理系统	并网点额定频率fN	范围： [0.000-100.000] Hz
10097	能量管理系统	应急FCAS动作死区fd	范围： (0.000-0.200] Hz，注意：应急FCAS动作死区fd(Hz) < 应急FCAS全量响应频差阈值fm(Hz)
10098	能量管理系统	应急FCAS最大输出有功功率PA	范围： (0.00-9999.99] MW
10099	能量管理系统	应急FCAS最大吸收有功功率PB	范围： (0.00-9999.99] MW
10100	能量管理系统	应急FCAS全量响应频差阈值fm	范围： (0.000-0.500] Hz
10038	储能逆变器&光伏逆变器	欠压一级保护值	光伏逆变器范围：最小值额定电压0.05倍，最大值额定电压1.0倍-0.1V；
储能逆变器范围：最小值460，最大值2300
10039	储能逆变器&光伏逆变器	过压一级保护值	光伏逆变器范围：最小值额定电压(1.0倍 + 0.2V)，最大值额定电压1.4倍；
储能逆变器范围：最小值2300，最大值2990
10040	储能逆变器&光伏逆变器	欠频一级保护值	光伏逆变器范围：最小值[50Hz电网:4500,60Hz电网非北美国家:5500,60Hz电网北美国家:5000]，最大值[50Hz电网:4996,60Hz电网非北美国家:5996,60Hz电网北美国家:5996]；
储能逆变器范围：最小值4500，最大值5000
10041	储能逆变器&光伏逆变器	过频一级保护值	光伏逆变器范围：最小值【50Hz电网: 5004，60Hz电网: 6004】，最大值【50Hz电网: 5500，60Hz电网: 6600】；
储能逆变器范围：最小值5000，最大值5550
10042	储能逆变器&光伏逆变器	过压保护恢复值	光伏逆变器范围：最小值1.0倍额定电压+0.1V，最大值1.4倍额定电压-0.1V；
储能逆变器范围：最小值2300，最大值2990
10043	储能逆变器&光伏逆变器	欠压保护恢复值	光伏逆变器范围：最小值额定电压(0.05倍+0.1V)，最大值额定电压1.0倍；储能逆变器范围：最小值1300，最大值2300
10044	储能逆变器&光伏逆变器	过频保护恢复值	光伏逆变器范围：最小值【50Hz电网: 5002 ，60Hz电网: 6002】，最大值【50Hz电网: 5498，60Hz电网: 6498】；
储能逆变器范围：最小值5000，最大值5550
10045	储能逆变器&光伏逆变器	欠频保护恢复值	光伏逆变器范围：最小值【50Hz电网: 4502，60Hz电网: 5502】，最大值【50Hz电网: 4998，60Hz电网: 5998】；
储能逆变器范围：最小值4450，最大值5000
10101	储能逆变器&光伏逆变器	欠压一级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，欠压一级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10102	储能逆变器&光伏逆变器	欠压二级保护值	范围依赖：额定电网电压，欠压二级保护值最大值=额定电网电压-1，欠压二级保护值最小值=额定电网电压*0.05；设置电网异常保护阈值和保护时间，电网公司提供了标准默认设置，一般无需更改。
10103	储能逆变器&光伏逆变器	欠压二级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，欠压二级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10104	储能逆变器&光伏逆变器	过压一级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，过压一级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10105	储能逆变器&光伏逆变器	过压二级保护值	范围依赖：额定电网电压，过压二级保护值最大值=额定电网电压*1.4，过压二级保护值最小值=额定电网电压+2；电网公司提供了标准默认设置，一般无需更改。
10106	储能逆变器&光伏逆变器	过压二级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，过压二级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10107	储能逆变器&光伏逆变器	欠频一级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，欠频一级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10108	储能逆变器&光伏逆变器	欠频二级保护值	50Hz电网范围：[4500-4996]Hz，60Hz非北美国家电网范围：[5500-5996]Hz，60Hz北美国家电网范围：[5000-5996]Hz
10109	储能逆变器&光伏逆变器	欠频二级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，欠频二级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10110	储能逆变器&光伏逆变器	过频一级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，过频一级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10111	储能逆变器&光伏逆变器	过频二级保护值	50Hz电网范围：[5004-5500]Hz；60Hz电网范围：[6004-6600]Hz；
10112	储能逆变器&光伏逆变器	过频二级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，过频二级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10113	储能逆变器&光伏逆变器	欠压三级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，欠压三级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10114	储能逆变器&光伏逆变器	过压三级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，过压三级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10115	储能逆变器&光伏逆变器	欠频三级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，欠频三级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10116	储能逆变器&光伏逆变器	过频三级保护时间	范围：[1-1440000]s；范围依赖：电网异常保护时间范围下限，过频三级保护时间最小值=电网异常保护时间范围下限；电网公司提供了标准默认设置，一般无需更改。
10117	储能逆变器&光伏逆变器	欠压三级保护值	范围依赖：额定电网电压，欠压三级保护值最大值=额定电网电压-1，欠压三级保护值最小值=额定电网电压*0.05；电网公司提供了标准默认设置，一般无需更改。
10118	储能逆变器&光伏逆变器	过压三级保护值	范围依赖：额定电网电压，过压三级保护值最大值=额定电网电压*1.4，过压三级保护值最小值=额定电网电压+2；电网公司提供了标准默认设置，一般无需更改。
10119	储能逆变器&光伏逆变器	欠频三级保护值	50Hz电网范围：[4500-4996]Hz，60Hz非北美国家范围:[5500-5996]Hz，60Hz北美国家电网范围:[5000-5996]Hz；电网公司提供了标准默认设置，一般无需更改。
10120	储能逆变器&光伏逆变器	过频三级保护值	50Hz电网范围：[4500-4996]Hz，60Hz国家范围:[5500-5996]Hz；电网公司提供了标准默认设置，一般无需更改。


逆变器常用测点
测点id	测点名称	单位
1	当日发电	Wh
87	当月发电	Wh
88	当年发电	Wh
2	总发电量	Wh
24	总有功功率	W
14	总直流功率	W
18	A相电压	V
19	B相电压	V
20	C相电压	V
21	A相电流	A
22	B相电流	A
23	C相电流	A
25	总无功功率	var
94	方阵绝缘阻抗	kΩ
27	电网频率	Hz
7356	总运行时间	h
15	A-B线电压	V
16	B-C线电压	V
17	C-A线电压	V
4	机内空气温度	℃
95	母线电压	V
26	总功率因数
120	AFCI故障次数
90	负极对地电压	V
43	总视在功率	VA
33	模块1温度	℃
34	模块2温度	℃
35	模块3温度	℃
36	模块4温度	℃
37	模块5温度	℃
38	模块6温度	℃
39	正极对地阻抗值	Ω
40	负极对地阻抗值	Ω
41	限功率实际值	W
42	无功调节实际值	va
67	日理论发电量	Wh
5	MPPT1电压	V
6	MPPT1电流	A
7	MPPT2电压	V
8	MPPT2电流	A
9	MPPT3电压	V
10	MPPT3电流	A
45	MPPT4电压	V
46	MPPT4电流	A
47	MPPT5电压	V
48	MPPT5电流	A
49	MPPT6电压	V
50	MPPT6电流	A
51	MPPT7电压	V
52	MPPT7电流	A
53	MPPT8电压	V
54	MPPT8电流	A
55	MPPT9电压	V
56	MPPT9电流	A
57	MPPT10电压	V
58	MPPT10电流	A
7401	MPPT11电压	V
7451	MPPT11电流	A
7402	MPPT12电压	V
7452	MPPT12电流	A
7723	MPPT13电压	V
7724	MPPT13电流	A
7725	MPPT14电压	V
7726	MPPT14电流	A
7727	MPPT15电压	V
7728	MPPT15电流	A
7729	MPPT16电压	V
7730	MPPT16电流	A
7731	MPPT17电压	V
7732	MPPT17电流	A
7733	MPPT18电压	V
7734	MPPT18电流	A
7735	MPPT19电压	V
7736	MPPT19电流	A
7737	MPPT20电压	V
7738	MPPT20电流	A
96	组串1电压	V
70	组串1电流	A
97	组串2电压	V
71	组串2电流	A
98	组串3电压	V
72	组串3电流	A
99	组串4电压	V
73	组串4电流	A
100	组串5电压	V
74	组串5电流	A
101	组串6电压	V
75	组串6电流	A
102	组串7电压	V
76	组串7电流	A
103	组串8电压	V
77	组串8电流	A
104	组串9电压	V
78	组串9电流	A
105	组串10电压	V
79	组串10电流	A
106	组串11电压	V
80	组串11电流	A
107	组串12电压	V
81	组串12电流	A
108	组串13电压	V
82	组串13电流	A
109	组串14电压	V
83	组串14电流	A
110	组串15电压	V
84	组串15电流	A
111	组串16电压	V
85	组串16电流	A
112	组串17电压	V
92	组串17电流	A
113	组串18电压	V
93	组串18电流	A
7166	组串19电压	V
313	组串19电流	A
7167	组串20电压	V
314	组串20电流	A
7168	组串21电压	V
315	组串21电流	A
7169	组串22电压	V
316	组串22电流	A
7170	组串23电压	V
317	组串23电流	A
7171	组串24电压	V
318	组串24电流	A
7172	组串25电压	V
319	组串25电流	A
7173	组串26电压	V
320	组串26电流	A
7174	组串27电压	V
321	组串27电流	A
7175	组串28电压	V
322	组串28电流	A
7176	组串29电压	V
323	组串29电流	A
7177	组串30电压	V
324	组串30电流	A
7178	组串31电压	V
325	组串31电流	A
7179	组串32电压	V
326	组串32电流	A
7707	组串33电压	V
7708	组串33电流	A
7709	组串34电压	V
7710	组串34电流	A
7711	组串35电压	V
7712	组串35电流	A
7713	组串36电压	V
7714	组串36电流	A
7715	组串37电压	V
7716	组串37电流	A
7717	组串38电压	V
7718	组串38电流	A
7719	组串39电压	V
7720	组串39电流	A
7721	组串40电压	V
7722	组串40电流	A
11	PV1功率	W
12	PV2功率	W
13	PV3功率	W
59	PV4功率	W
60	PV5功率	W
61	PV6功率	W
62	PV7功率	W
63	PV8功率	W
64	PV9功率	W
65	PV10功率	W
3	总并网运行时间	h
29	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网充电，6144-智能建站状态，20-微网运行	
更多开放测点定义信息通过getOpenPointInfo接口获取。

电站常用测点
测点id	测点名称	单位
83022	电站日发电量	Wh
83024	电站累计发电	Wh
83033	电站功率	W
83019	电站功率/电站装机功率
83006	电表日发电量	Wh
83020	电表累计发电	Wh
83011	电表日用电量	Wh
83021	电表累计用电	Wh
83032	电表交流功率	W
83002	逆变器交流功率	W
83004	逆变器累计发电	Wh
83009	逆变器日发电量	Wh
83012	电站瞬时辐照	W/㎡
83013	电站日辐射量	Wh/㎡
83023	电站PR
83025	电站等效小时	h
83005	电表日等效小时	h
83007	电表PR
83018	日理论发电量	Wh
83001	逆变器交流功率归一化	W/Wp
83008	逆变器日等效小时	h
83010	逆变器PR
83016	电站环境温度	℃
83017	电站组件温度	℃
83046	PCS总有功功率	W
83052	负载功率	W
83067	PV总有功功率	W
83097	日直接消耗电量	Wh
83100	总直接消耗电量	Wh
83102	今日取电	Wh
83105	累计取电	Wh
83106	负载功率	W
83118	日负载用电	Wh
83124	总负载用电	Wh
83119	日PV馈网电量	Wh
83072	今日馈网	Wh
83075	累计馈网	Wh
83252	电池电量
83129	电池SOC
83232	全场SOC
83233	全场最大可充电功率	W
83234	全场最大可放电功率	W
83235	全场可充电量	Wh
83236	全场可放电量	Wh
83237	全场储能最大无功功率	W
83238	全场储能总有功功率	W
83239	全场总无功功率	var
83240	全场功率因数
83241	全场总充电量	Wh
83242	全场总放电量	Wh
83243	全场日充电量	Wh
83244	全场日放电量	Wh
83548	累计充放电次数
83549	电网有功功率	W
83419	逆变器当日最大功率/逆变器装机容量
83317	预测功率	W
83318	储能充放电功率计划值	W
83319	储能SOC计划值	W
83320	计划可充电量	Wh
83321	计划可放电量	Wh
83322	储能日充电量(EMS)	Wh
83323	储能日放电量(EMS)	Wh
83324	储能累计充电量	Wh
83325	累计放电量	Wh
83326	储能有功功率(EMS)	W
83327	储能剩余电量	Wh
83328	电网有功功率(EMS)	W
83329	光伏有功功率(EMS)	W
83330	负载有功功率(EMS)	W
83331	光伏日发电量(EMS)	Wh
83332	光伏总发电量	Wh
83334	储能SOC(EMS)
83743	日限电损失电量	Wh
更多开放测点定义信息通过getOpenPointInfo接口获取。

汇流箱常用测点
测点id	测点名称	单位
1005	总直流电流	A
1001	直流母线电压	V
1006	总直流功率	W
1002	机内温度	℃
1009	第1路电流	A
1010	第2路电流	A
1011	第3路电流	A
1012	第4路电流	A
1013	第5路电流	A
1014	第6路电流	A
1015	第7路电流	A
1016	第8路电流	A
1017	第9路电流	A
1018	第10路电流	A
1019	第11路电流	A
1020	第12路电流	A
1021	第13路电流	A
1022	第14路电流	A
1023	第15路电流	A
1024	第16路电流	A
1025	第17路电流	A
1026	第18路电流	A
1027	第19路电流	A
1028	第20路电流	A
1029	第21路电流	A
1030	第22路电流	A
1031	第23路电流	A
1032	第24路电流	A
更多开放测点定义信息通过getOpenPointInfo接口获取。

环境检测仪常用测点
测点id	测点名称	单位
2003	平面瞬时辐照	W/㎡
10821	平面日辐射量	Wh/㎡
2002	平面总辐射量	Wh/㎡
2007	斜面瞬时辐照	W/㎡
2005	斜面日辐射量	Wh/㎡
2006	斜面总辐射量	Wh/㎡
2009	环境温度	℃
2010	组件温度	℃
2016	风速	m/s
2011	风速等级
2012	风向度数	°
2014	大气压力	hPa
2015	环境湿度	%RH
2022	雨量	mm
2026	降水量	mm
2100	温度1（背板温度）	℃
2101	温度2	℃
2102	温度3	℃
2103	温度4	℃
2104	温度5	℃
2105	露点
2106	土湿1
2107	土湿2
2108	土湿3
2109	CO₂
2110	蒸发
2111	总辐射1瞬时值
2112	散射辐射瞬时值
2113	直接辐射瞬时值
2114	总辐射2瞬时值
2115	净辐射瞬时值
2116	光合辐射瞬时值
2117	紫外辐射瞬时值
2118	风向瞬时值
2119	风速瞬时值
2120	2分钟风速
2121	10分钟风速
2122	雨量时间间隔累计值
2123	日照时间间隔累计值
2124	总辐射1时间间隔累计值
2125	散射辐射时间间隔累计值
2126	直接辐射时间间隔累计值
2127	总辐射2时间间隔累计值
2128	净辐射时间间隔累计值
2129	光合辐射时间间隔累计值
2130	紫外辐射时间间隔累计值
2131	雨量日累计
2132	日照日累计
2133	总辐射1日累计值
2134	散射辐射日累计值
2135	直接辐射日累计值
2136	总辐射2日累计值
2137	净辐射日累计值
2138	光合辐射日累计值
2139	紫外辐射日累计值

电表常用测点
测点id	测点名称	单位
8030	正向有功电度	Wh
8031	反向有功电度	Wh
8062	日正向有功电度	Wh
8063	日反向有功电度	Wh
8032	正向无功电度	varh
8033	反向无功电度	varh
8034	峰正向有功电度	Wh
8035	峰反向有功电度	Wh
8038	谷正向有功电度	Wh
8039	谷反向有功电度	Wh
8042	平正向有功电度	Wh
8043	平反向有功电度	Wh
8058	尖正向有功电度	Wh
8059	尖反向有功电度	Wh
8036	峰正向无功电度	Wh
8037	峰反向无功电度	Wh
8040	谷正向无功电度	Wh
8041	谷反向无功电度	Wh
8044	平正向无功电度	Wh
8045	平反向无功电度	Wh
8060	尖正向无功电度	Wh
8061	尖反向无功电度	Wh
8000	A相电压	V
8001	B相电压	V
8002	C相电压	V
8003	A-B线电压	V
8004	B-C线电压	V
8005	C-A线电压	V
8006	A相电流	A
8007	B相电流	A
8008	C相电流	A
8064	频率	Hz
8018	电表有功功率	W
8022	无功功率	var
8014	功率因数
8026	视在功率	VA
8076	电表A相有功功率	W
8077	电表B相有功功率	W
8078	电表C相有功功率	W
8084	日直接消耗电量	Wh
8085	总直接消耗电量	Wh

通信装置常用测点
测点id	测点名称	单位
10555	AI电压信号1	V
10575	AI电流信号1	mA
10557	AI电压信号2	V
10576	AI电流信号2	mA
10559	AI电压信号3	V
10577	AI电流信号3	mA
10561	AI电压信号4	V
10578	AI电流信号4	mA
10563	PT信号1	℃
10565	PT信号2	℃
10567	DO信号1
10569	DO信号2
10571	DO信号3
10573	DO信号4
10026	总功率	W
10028	总发电量	Wh
10046	总无功功率	var
10510	移动网络信号强度
10511	WLAN信号强度
10587	总有功功率	W

储能逆变器常用测点
测点id	测点名称	单位
13011	有功功率	W
13003	总直流功率	W
13157	A相电压	V
13158	B相电压	V
13159	C相电压	V
13008	A相电流	A
13009	B相电流	A
13010	C相电流	A
13012	总无功功率	var
13160	方阵绝缘阻抗	kΩ
13007	电网频率	Hz
18065	离网口A相功率	W
18066	离网口B相功率	W
18067	离网口C相功率	W
18068	离网口总功率	W
18062	离网口A相电流	A
18063	离网口B相电流	A
18064	离网口C相电流	A
13020	总运行时间	H
13134	总PV发电量	Wh
13112	日PV发电量	Wh
13187	交流电压	V
13188	交流电流	A
13004	A-B线电压	V
13005	B-C线电压	V
13006	C-A线电压	V
13019	机内空气温度	℃
13161	母线电压	V
13013	总功率因数
13001	MPPT1电压	V
13002	MPPT1电流	A
13105	MPPT2电压	V
13106	MPPT2电流	A
13107	MPPT3电压	V
13108	MPPT3电流	A
13109	MPPT4电压	V
13110	MPPT4电流	A
13122	今日馈网	Wh
13125	累计馈网	Wh
13147	今日取电	Wh
13148	累计取电	Wh
13149	电网取电功率	W
13121	馈网功率	W
13173	今日PV馈网	Wh
13175	累计PV馈网	Wh
13141	电池电量
13029	今日电池放电	Wh
13028	今日电池充电	Wh
13138	电池电压	V
13139	电池电流	A
13035	累计电池放电	Wh
13034	累计电池充电	Wh
13142	电池健康度
13143	电池温度	℃
13162	最大充电电流(BMS)	A
13163	最大放电电流(BMS)	A
13174	今日PV电池充电	Wh
13176	累计PV电池充电	Wh
13126	电池充电功率	W
13150	电池放电功率	W
13199	日负载用电	Wh
13137	总直接消耗电量	Wh
13119	负载功率	W
13130	总负载用电	Wh
13116	日直接消耗电量	Wh
13144	日自发自用率
13016	总充电时间	H
13017	总放电时间	H
13018	总视在功率	VA
13023	日充电时间	H
13024	日放电时间	H
13118	年直接消耗电量	Wh
13165	MDSP离网启机状态
13166	SDSP工作模式
13167	SDSP离网启机状态
13168	DI状态
13169	电池电压（BMS）	V
13170	电池SOC（BMS）
13171	EMS状态
13172	日自给自足率
13140	电池容量(kWh)	Wh
18075	通道二总视在功率	VA
18076	通道二A相视在功率	VA
18077	通道二B相视在功率	VA
18078	通道二C相视在功率	VA
18079	通道二总有功功率	W
18080	通道二A相有功功率	W
18081	通道二B相有功功率	W
18082	通道二C相有功功率	W
18083	通道二总无功功率	var
18084	通道二A相无功功率	var
18085	通道二B相无功功率	var
18086	通道二C相无功功率	var
18087	通道二功率因数
18088	通道二总取电电量	Wh
18089	通道二A相取电电量	Wh
18090	通道二B相取电电量	Wh
18091	通道二C相取电电量	Wh
18092	通道二总馈网电量	Wh
18093	通道二A相馈网电量	Wh
18094	通道二B相馈网电量	Wh
18095	通道二C相馈网电量	Wh
18103	离网口A相电压	V
18104	离网口B相电压	V
18105	离网口C相电压	V
18108	电表A相电压	V
18109	电表B相电压	V
18110	电表C相电压	V
13146	运行状态，0-并网运行，1024-维护模式运行，2048-强制模式运行，4096-离网运行，8192-开环，16384-能量调度运行，16385-紧急充电运行，4369-未初始化，32768-停机，4864-按键关机，5376-紧急停机，5120-待机，4608-初始待机，5632-启动中，37120-告警运行，33024-降额运行，33280-调度运行，21760-故障停机，5888-AFCI自检，1-停机，2-按键关机，4-紧急停机，8-待机，16-初始待机，32-启动中，64-逆变器已并网正常运行，128-降额运行，256-运行故障，512-升级失败，9472-LCD与DSP通信故障，9473-重启中，16435-绝缘阻抗低，16439-绝缘板异常，20992-关机中，33792-反PID运行，6400-安全模式，65-离网直流充电，20-微网运行	

通讯模块常用测点
测点id	测点名称	单位
23001	无线信号强度
23014	WLAN信号强度
23008	卡号


电池常用测点
测点id	测点名称	单位
58601	电池电压	V
58602	电池电流	A
58603	电池温度	℃
58604	电池剩余电量
58605	电池健康度
58606	累计电池充电	Wh
58607	累计电池放电	Wh
58608	电池运行状态
58609	标准健康状态
58610	电芯电压最大值	mV
58611	电芯电压最大值位置
58612	电芯电压最小值	mV
58613	电芯电压最小值位置
58614	模组温度最高值	℃
58615	模组温度最高值位置
58616	模组温度最低值	℃
58617	模组温度最低值位置
58618	模组1电芯电压最大值	mV
58619	模组2电芯电压最大值	mV
58620	模组3电芯电压最大值	mV
58621	模组4电芯电压最大值	mV
58622	模组5电芯电压最大值	mV
58623	模组6电芯电压最大值	mV
58624	模组7电芯电压最大值	mV
58625	模组8电芯电压最大值	mV
58626	模组1电芯电压最小值	mV
58627	模组2电芯电压最小值	mV
58628	模组3电芯电压最小值	mV
58629	模组4电芯电压最小值	mV
58630	模组5电芯电压最小值	mV
58631	模组6电芯电压最小值	mV
58632	模组7电芯电压最小值	mV
58633	模组8电芯电压最小值	mV
58635	直流接触器状态
58636	故障模组位置

EMS设备常用测点
测点id	测点名称	单位
24620	储能日充电量	Wh
24621	储能日放电量	Wh
24622	储能总充电量	Wh
24623	储能总放电量	Wh
24624	光伏有功功率	W
24625	储能有功功率	W
24626	电网有功功率	W
24627	光伏日发电量	Wh
24628	光伏总发电量	Wh
24629	储能SOC	%
24630	储能剩余电量	Wh
24631	有功负载	W


LC设备常用测点
测点id	测点名称	单位
59502	软件版本
59535	总充电量	Wh
59536	总放电量	Wh
59541	总有功功率	W
59542	总无功功率	var
59546	日充电量	Wh
59547	日放电量	Wh
59551	工作模式
59552	系统工作状态
59705	设备S/N

PCS设备常用测点
测点id	测点名称	单位
44010	整机总有功功率	W
44011	整机总无功功率	var
44012	整机功率因数
44025	工作模式
44029	整机电网频率	Hz
44231	运行状态
44244	机内空气温度	℃
44803	设备S/N
44823	PCS-DSP版本号
44824	PCS-CPLD版本号


CMU设备常用测点
测点id	测点名称	单位
59002	总电压
59003	总电流
59004	SOC
59006	电池总容量
59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59403	软件版本


BSC设备常用测点
测点id	测点名称	单位
59008	最高电池单体电压	mV
59010	最低电池单体电压	mV
59012	最高电池单体温度	℃
59014	最低电池单体温度	℃
59064	最高电芯电压位置(#BMU~#Cell)
59065	最低电芯电压位置(#BMU~#Cell)
59066	最高电芯温度位置(#BMU~#Cell)
59067	最低电芯温度位置(#BMU~#Cell)


充电桩常用测点
测点id	测点名称	单位
33708	充电功率	kW
33722	最小充电功率	kW
33723	最大充电功率	kW
33702	A相充电电压	V
33704	B相充电电压	V
33706	C相充电电压	V
33710	CP电压	V
33707	C相充电电流	A
33705	B相充电电流	A
33703	A相充电电流	A
33728	最大充电电流	A
33729	最小充电电流	A
33716	充电状态	空闲(未插枪):1-- 待机(已插枪):2--充电中:3--充电暂停(桩端):4--充电暂停(车端):5--充电完成:6--预约:7--禁用:8--故障:9


微逆常用测点
测点id	测点名称	单位
51301	运行状态（21760:故障停机,0:并网运行,1024:维护模式运行,2048:强制模式运行,4096:离网运行,8192:开环,4608:初始待机,32768:停机,5120:待机,5632:启动中,33024:降额运行,33280:调度运行,4369:初始状态,4864:按键关机,37120:告警运行）
51302	总发电量	Wh
51303	总有功功率	W
51304	总无功功率	var
51305	总直流功率	W
51306	总视在功率	VA
51307	总功率因数
51308	电网频率	Hz
51309	交流电压	V
51312	交流电流	A
51315	PV1电压	V
51316	PV1电流	A
51317	PV2电压	V
51318	PV2电流	A
51319	PV3电压	V
51320	PV3电流	A
51321	PV4电压	V
51322	PV4电流	A
51323	PV5电压	V
51324	PV5电流	A
51325	PV6电压	V
51326	PV6电流	A
51333	PV1功率	W
51334	PV2功率	W
51335	PV3功率	W
51336	PV4功率	W
51337	PV5功率	W
51338	PV6功率	W
51339	PV1累计发电	Wh
51340	PV2累计发电	Wh
51341	PV3累计发电	Wh
51342	PV4累计发电	Wh
51343	PV5累计发电	Wh
51344	PV6累计发电	Wh
51346	当日发电	Wh
51347	PV1当日发电	Wh
51348	PV2当日发电	Wh
51349	PV3当日发电	Wh
51350	PV4当日发电	Wh
51351	PV5当日发电	Wh
51352	PV6当日发电	Wh
更多开放测点定义信息通过getOpenPointInfo接口获取。