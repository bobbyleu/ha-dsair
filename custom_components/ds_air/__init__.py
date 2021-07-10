"""
Platform for DS-AIR of Daikin
https://www.daikin-china.com.cn/newha/products/4/19/DS-AIR/
"""
# from custom_components.ds_air.ds_air_service.decoder import decoder
# from custom_components.ds_air.ds_air_service.display import display
# from custom_components.ds_air.ds_air_service.param import *
# from custom_components.ds_air.ds_air_service.service import Service, SocketClient
#
# Service.init('192.168.1.103', 8008)
# for aircon in Service.get_new_aircons():
#     print("###############3", aircon.alias)
# # sc = SocketClient('192.168.1.103', 8008)
# # sc.send(AirConRecommendedIndoorTempParam())
#
#
# def num(s):
#     if '0' <= s <= '9':
#         return int(s)
#     return ord(s) - 97 + 10
#
#
# def calc(s):
#     return num(s[0]) * 16 + num(s[1])
#
#
# def disp(t, s):
#     if s[0] == 'D':
#         s = s[6:]
#     e = Encode()
#     i = 0
#     l = len(s)
#     while i < l:
#         e.write1(calc(s[i:i + 2]))
#         i = i + 2
#     r, b = decoder(e.pack(False))
#     print('\033[1;35m' + t + '\033[0m', display(r))


# disp('s206', 'Data: 0210000d0000000100000000000000000100a003')  # 206 hand shake
# disp('r221', 'Data: 0211000d0000000100000000000000000001000203')  # 221
# disp('r223', 'Data: 021e000d0000000100000000000000000000a0323032313037313030323133313603')  # 223 handshake
# disp('s250', 'Data: 0210000d00000002000000000000000001500003')  # 250
# disp('r251', 'Data: 0211000d0000000200000000000000000001000203')  # 251
# disp('r253', '026f000d0000000200000000000000000050000830322e30392e303000601803096b3b0d3139322e3136382e312e3130330d3235352e3235352e3235352e300b3139322e3136382e312e310b3139322e3136382e312e310f3131342e3131342e3131342e31313407e507070a020d1000000003')  #253
# disp('s256', 'Data: 0213000d00010003000000000000000001300001ffff03')  # get room info
# disp('s257', 'Data: 0210000d00000004000000000000000001c90003')  #
# disp('r258', 'Data: 0211000d0000000300000000000000000001000203')  #
# disp('r260', 'Data: 022c010d00010003000000000000000000300006000602000304312d303106e9a490e58e8508382d34302e706e67010017000000010004312d303104312d303103000304312d303206e5aea2e58e8508382d34352e706e67010017000000010004312d303204312d303204000304312d303306e5aea2e58da708382d35312e706e67010017000000010004312d303304312d303305000304312d303406e4b8bbe58da708382d34372e706e67010017000000010004312d303404312d303406000304312d303506e4b9a6e688bf08382d35302e706e67010017000000010004312d303504312d30352100030b73656e736f72736b6974320ce79b91e6b58be4b8ade5bf8308382d33332e706e6701001900000001000c3463313161653938623664630c34633131616539386236646303')  #
# disp('r262', '0211000d00000004000000000000000000010002030211000d00000004000000000000000000c9000103')  #
# disp('s268', 'Data: 0211000d000000060000000819000000015900ff03')  # sensor info
# disp('s269', 'Data: 0212000d000000050000000a2f000000000400ff0103')  # AIR_RECOMMENDED_INDOOR_TEMP
# disp('s270', 'Data: 0210000d000000070000000a3000000001010003')  # SLEEP_SENSOR_LIST
# disp('r271', 'Data: 0211000d0000000600000000000000000001000203')  #
# disp('r274', '0255000d0000000600000008190000000059000101214103004c11ae98b6dc0c3463313161653938623664637f000601f001060096030101000000011801ff7fff7fff7f4b000000e8030000023c000a0001010116000800030211000d000000050000000a2f00000000040000030211000d00000007000000000000000000010002030211000d000000070000000a300000000001000003')  #SENSOR2_INFO
# disp('s276', 'Data: 0211000d000000090000000819000000015900ff03')  # sensor info
# disp('s277', '0220000d00000008000000081700000001060005020100030100040100050100060100030211000d0000000a0000000000000000012300ff03')  #
# disp('s278', '0212000d000000100000000a2f000000000400ff01030213000d0000000b0000000817000000010300020077030213000d0000000c0000000817000000010300030077030213000d0000000d0000000817000000010300040077030213000d0000000e0000000817000000010300050077030213000d0000000f0000000817000000010300060077030210000d000000110000000a30000000010100030210000d000000120000000831000000010a0003')  #
# disp('r282', '0255000d0000000900000008190000000059000101214103004c11ae98b6dc0c3463313161653938623664637f000601f001060096030101000000011801ff7fff7fff7f4b000000e8030000023c000a0001010116000800030211000d0000000800000000000000000001000203022f000d00000008000000081700000000060005020100a31f87030100a31f87040100a31f87050100a31f87060100a31f87030211000d0000000a00000000000000000001000203027f000d0000000a0000000000000000002300050201000101000401000901100a01200b01100c0120000301000101000401000901100a01200b01100c0120000401000101000401000901100a01200b01100c0120000501000101000401000901100a01200b01100c0120000601000101000401000901100a01200b01100c012000030211000d000000100000000a2f00000000040000030211000d0000000b00000000000000000001000203021a000d0000000b000000081700000000030002007700000504016601030211000d0000000c00000000000000000001000203021a000d0000000c0000000817000000000300030077000604fa006602030211000d0000000d00000000000000000001000203021a000d0000000d000000081700000000030004007700000018011701030211000d0000000e00000000000000000001000203021a000d0000000e00000008170000000003000500770107000e016601030211000d0000000f00000000000000000001000203021a000d0000000f00000008170000000003000600770100050e016601030211000d00000011000000000000000000010002030211000d000000110000000a3000000000010000030211000d00000012000000000000000000010002030211000d000000120000000831000000000a000003')  #
# disp('s284', 'Data: 0210000d00000013000000000000000001ca0003')  #
# disp('r287', 'Data: 0211000d00000013000000000000000000ca000003')  #
# disp('s290', 'Data: 0214000d0001001400000000000000000130000121000203')  #
# disp('r293', '0238000d00010014000000000000000000300006000121000201001900000001000c3463313161653938623664630c34633131616539386236646303')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #
# disp('', '')  #

# print('***********************')
