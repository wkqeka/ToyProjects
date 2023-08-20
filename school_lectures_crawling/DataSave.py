import openpyxl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from time import sleep

# 엑셀 잠시 다뤄보기
# 엑셀에 값 추가하고 저장하기
# 일단 한 곳에 몰아놓고 1학년 2학년 3학년 4학년 다 분리하기
def SaveData(dr, size, SubjectWorkbook):
    # excel 파일에 학과를 돌리면서 수집한 데이터를 저장하면서 반복문을 돌린다
    # 파일 위치 지정 후 학과를 바꿔준다
    # 학과를 바꾸면서 모든 데이터를 긁어와야 되는데 이걸 어케 해야할지 정해야 함
    if(size == -1):
        return
    
    SheetFirst = SubjectWorkbook["원본"]
    html = dr.page_source
    soup = BeautifulSoup(html, 'html.parser')
    Lectures = soup.select('#CP1_grdView tbody tr')
    # 강의 목록 최대 10개
    # find all로 묶어서 처리해보자!
    
    for pageindex in range(1, size,1):
        sleep(0.2)
        html = dr.page_source
        soup = BeautifulSoup(html, 'html.parser')
        Lectures = soup.select('#CP1_grdView tbody tr')
        DataList = []
        
        for data in Lectures:
            DataList.extend(data.stripped_strings)
        
        for row in range(0,int(len(DataList)/14),1):
            for col in range(0,14,1):   
                SheetFirst.cell(row + 2,col + 1).value = DataList[col]
        
        dr.find_element(By.XPATH, f'//*[@id="CP1_COM_Page_Controllor1_lbtnPage{pageindex}"]').click()

    SubjectWorkbook.save('D:/Projects/PythonApplication1/test1.xlsx')

        # //*[@id="CP1_COM_Page_Controllor1_lbtnPage2"]
        # //*[@id="CP1_COM_Page_Controllor1_lbtnPage1"]
    
    # ['대학', '교양', '100105', '001', '세계', '2.00', '2', '사이버강좌', 'teacher', '', 'Y', '', '0', '수업계획서', '2023', '20', '100105', '001', '12309', '세계', '인원초과']

def DefaultSetting(SubjectWorkbook, FileName):
    # 시트 이름, 시트에 head부분 저장
    SubjectWorkbook.active.title = "원본"
    SheetFirst = SubjectWorkbook["원본"]

    head = ['개설학과', '이수구분', '과목번호', '분반', '교과목명'
        , '학점/시간', '수강', '학년', '강의실(시간)', '담당교수', '원어강의'
        , '원격', '강의', '교양영역', '제한', '인원', '수업계획서', '비고'] # 14개
    for i in range(1,len(head) + 1):
        SheetFirst.cell(1,i).value = head[i - 1]

    SubjectWorkbook.save(FileName)


