# SauceDemo 自动化测试用例集

| 用例编号 | 模块 | 测试场景 | 前置条件 | 操作步骤 | 预期结果 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TC-LOGIN-01 | 登录 | 锁定账号登录 | 打开登录页 | 输入 `locked_out_user` / `secret_sauce`，点击登录 | 提示 "Sorry, this user has been locked out" |
| TC-LOGIN-02 | 登录 | 密码错误 | 同上 | 输入 `standard_user` / `wrong_pwd` | 提示 "Username and password do not match" |
| TC-LOGIN-03 | 登录 | 账号为空 | 同上 | 账号留空，密码 `secret_sauce` | 提示 "Username is required" |
| TC-LOGIN-04 | 登录 | 密码为空 | 同上 | 账号 `standard_user`，密码留空 | 提示 "Password is required" |
| TC-LOGIN-05 | 登录 | 账号不存在 | 同上 | 输入 `invalid_user` / `secret_sauce` | 提示用户名密码不匹配 |
| TC-INV-01 | 商品 | 页面标题验证 | 正常登录后 | 查看页面顶部标题 | 标题显示 "Products" |
| TC-INV-02 | 商品 | 价格排序 | 正常登录后 | 下拉选择 "Price (low to high)" | 商品列表按价格升序排列 |
| TC-INV-03 | 商品 | 加购背包 | 正常登录后 | 点击 `Sauce Labs Backpack` 的 Add to cart | 按钮变为 Remove，角标显示 1 |
| TC-INV-04 | 商品 | 加购自行车灯 | 正常登录后 | 点击 `Sauce Labs Bike Light` 的 Add to cart | 角标数字继续累加 |
| TC-INV-05 | 商品 | 点击购物车图标 | 正常登录后 | 点击右上角购物车图标 | 页面跳转至 `/cart.html` |
| TC-CART-01 | 购物车 | 商品一致性 | 购物车内有商品 | 查看购物车列表中的商品名称 | 名称与加购时一致 |
| TC-CART-02 | 购物车 | 继续购物 | 购物车页 | 点击 "Continue Shopping" | 页面返回商品列表页 |
| TC-CART-03 | 购物车 | 进入结算 | 购物车内有商品 | 点击 "Checkout" | 页面跳转至结算信息填写页 |
| TC-CART-04 | 购物车 | 移除商品 | 购物车内有商品 | 点击对应商品的 "Remove" | 商品从列表消失 |
| TC-CART-05 | 购物车 | UI元素检查 | 购物车页 | 检查 Checkout 按钮状态 | 按钮可见且可点击 |
| TC-CHK-01 | 结算 | 姓名为空 | 进入结算页 | First Name 留空，点击 Continue | 提示 "Error: First Name is required" |
| TC-CHK-02 | 结算 | 姓氏为空 | 进入结算页 | Last Name 留空，点击 Continue | 提示 "Error: Last Name is required" |
| TC-CHK-03 | 结算 | 邮编为空 | 进入结算页 | Zip Code 留空，点击 Continue | 提示 "Error: Postal Code is required" |
| TC-CHK-04 | 结算 | 填写信息通过 | 进入结算页 | 正确填写姓名与邮编，点击 Continue | 跳转至订单确认页 (Checkout Step 2) |
| TC-CHK-05 | 结算 | 完成下单 | 订单确认页 | 点击 "Finish" 按钮 | 页面显示 "Thank you for your order!" |