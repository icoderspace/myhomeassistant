#我的Home Assistant控件和配置

中国工作日，HA中自带了一个holiday的控件，但是没有中国的。。。
所以访问 http://www.k780.com 的API写了一个判断中国工作日的控件，试了一下包括19年五一这种比较奇葩的放假规定都可以支持。
copy custom_components 文件夹到HA的配置目录

configuration.yaml文件里添加：

```binary_sensor:
  - platform: china_holiday
    api_key: 10003
    token: b59bc3ef6191eb9f747dd4e83c99f2a4
```
    
自动化添加里可以这样使用：
```
condition: 
    condition: state
    entity_id: binary_sensor.gong_zuo_ri
    state: '工作日/休息日'
```