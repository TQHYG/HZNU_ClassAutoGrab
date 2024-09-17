from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
import time
import captcha_solver  # 导入验证码识别库

# 设置 Edge 浏览器驱动路径
driver_path ='C:/dev/edgedriver_win64/msedgedriver.exe'
service = Service(executable_path=driver_path)
driver = webdriver.Edge(service=service)

#教务系统用户名与密码
username="username"
password="password"


# 打开课程网站
driver.get('http://jwxt.hznu.edu.cn/jwglxt/xtgl/login_slogin.html')

# 等待页面加载
wait = WebDriverWait(driver, 2)

# 登录操作函数
def login():
    username = wait.until(EC.presence_of_element_located((By.ID, 'yhm')))
    password = wait.until(EC.presence_of_element_located((By.ID, 'mm')))
    login_button = wait.until(EC.presence_of_element_located((By.ID, 'dl')))

    username.send_keys(username)
    password.send_keys(password)

    # 获取并输入验证码
    captcha_image = wait.until(EC.presence_of_element_located((By.ID, 'yzmPic')))
    captcha_image.screenshot('captcha.png')
    captcha_code = captcha_solver.solve_captcha('captcha.png')  # 使用验证码识别库
    #captcha_code = input("请输入验证码 (查看 captcha.png 文件): ")

    captcha_input = wait.until(EC.presence_of_element_located((By.ID, 'yzm')))
    captcha_input.send_keys(captcha_code)

    login_button.click()

# 循环尝试登录，直到成功
logged_in = False
while not logged_in:
    try:
        login()
        # 等待登录完成并跳转到课程选择页面
        wait.until(EC.url_contains('index_initMenu.html'))
        logged_in = True
    except:
        # 如果登录失败，刷新页面并重新尝试
        driver.refresh()


print("登录成功")

# 登录成功后直接导航到选课页面
driver.get('http://jwxt.hznu.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default')
print("已加载选课页面")


g_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '通识选修课')]")))
g_button.click()
# 点击“查询”按钮以加载课程列表
query_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@name='query']")))
query_button.click()





# 循环点击“点此查看更多”按钮，直到出现“已到最后”的字样或达到最大尝试次数
def full_load_list():
    max_attempts = 12
    attempts = 0
    while attempts < max_attempts:
        try:
            more_button = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '点此查看更多')]")))
            attempts += 1
            more_button.click()
            #time.sleep(1)  # 等待1秒后再检查
        except:
            try:
                end_sign = driver.find_element(By.XPATH, "//div[@id='endsign' and contains(text(), '已到最后')]")
                if end_sign:
                    break
            except:
                pass
    print("页面加载完成")

full_load_list()

#通识选修课id和体育课id
gcourse=['(2024-2025-1)-201202104-01','(2024-2025-1)-011202103-01','(2024-2025-1)-073049001-01']
pecourse=['(2024-2025-1)-06012-28','(2024-2025-1)-06012-29','(2024-2025-1)-06012-27']
selected_courses = []
failed_courses = []


 # 展开全部
def expand_all():
    full_load_list()
    # 使用CSS选择器查找所有具有指定类和属性的<a>元素
    expand_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href="javascript:void(0);"].expand_close.expand1')

    # 遍历所有找到的元素并点击
    for element in expand_elements:
        try:
            element.click()
        finally:
            continue
    driver.execute_script("""
        var elements = document.querySelectorAll('div.panel-body.table-responsive');
        for (var i = 0; i < elements.length; i++) {
            elements[i].setAttribute('style', 'display: block;');
        }
    """)

# 尝试选择通识选修课
g_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '通识选修课')]")))
g_button.click()

expand_all()
for course_id in gcourse:
    class_id = "("+course_id[14:23]+")"  # 提取班级ID
    try:
        
        # 查找课程ID并点击“选课”按钮
        course_row = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{course_id}')]/ancestor::tr")))
        select_button = course_row.find_element(By.XPATH, ".//button[contains(text(), '选课')]")
        select_button.click()
        selected_courses.append(course_id)
    except:
        failed_courses.append(course_id)

# 如果没有成功选择任何通识选修课，刷新页面并重新尝试
while not selected_courses:
    driver.refresh()
    time.sleep(1)
    g_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '通识选修课')]")))
    g_button.click()
    query_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@name='query']")))
    query_button.click()
    full_load_list()

    expand_all()
    for course_id in gcourse:
        class_id = "("+course_id[14:23]+")"  # 提取班级ID
        try:
            # 查找班级ID并点击“展开关闭”按钮
            class_row = wait.until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{class_id}')]")))
            expand_button = class_row.find_element(By.XPATH, ".//a[contains(@class, 'expand_close')]")
            expand_button.click()
            print("已展开")
            
            # 查找课程ID并点击“选课”按钮
            course_row = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{course_id}')]/ancestor::tr")))
            select_button = course_row.find_element(By.XPATH, ".//button[contains(text(), '选课')]")
            select_button.click()
            print("成功选择一项课程")
            selected_courses.append(course_id)
            continue
        except:
            failed_courses.append(course_id)
            continue

# 切换到体育分项
pe_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '体育分项')]")))
pe_button.click()
expand_all()
# 尝试选择体育分项
for course_id in pecourse:
    class_id = "("+course_id[14:23]+")"  # 提取班级ID
    try:

        
        # 查找课程ID并点击“选课”按钮
        course_row = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{course_id}')]/ancestor::tr")))
        select_button = course_row.find_element(By.XPATH, ".//button[contains(text(), '选课')]")
        select_button.click()
        selected_courses.append(course_id)
        continue
    except:
        failed_courses.append(course_id)
        continue


# 打印选课结果
print("已成功选择的课程:", selected_courses)
print("未能选择的课程:", failed_courses)

# 关闭浏览器
driver.quit()
