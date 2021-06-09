import streamlit as st
from SessionState import get
import pandas as pd
import numpy as np
import datetime, pymysql
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go

from konlpy import init_jvm
from konlpy.tag import Okt
import gensim
from gensim.models import Phrases
from generate_network import draw_networkx
import itertools
import re
from collections import Counter
import networkx as nx
#from PIL import Image
import webbrowser
def _call_db_info():
    return pymysql.connect(
        host = '183.111.204.69',
        port= 13306,
        user = 'newsbot1',
        password='lgensol2020!',
        db = 'news',
        charset = 'utf8')



# st.set_page_config(layout="wide")
st.set_page_config(page_title='News', page_icon=":heart:", layout='wide', initial_sidebar_state='auto')
#today = datetime.today()

max_width = 1200
padding_top =0
padding_bottom = 0
padding_left =0
padding_right =0
COLOR = '#A50135'
BACKGROUND_COLOR ='#f1f1f1'

def main():
    st.markdown(
            f"""
    <style>
        .reportview-container .main .block-container{{
            max-width: {max_width}px;
            padding-top: {padding_top}rem;
            padding-right: {padding_right}rem;
            padding-left: {padding_left}rem;
            padding-bottom: {padding_bottom}rem;
        }}
        .reportview-container .main {{
            color: {COLOR};
            background-color: {BACKGROUND_COLOR};
        }}
    </style>
    """,
            unsafe_allow_html=True,
    )
    #image = Image.open('/img/LGES_ver00.jpg')
    #st.title('News Summary Report')
    st.sidebar.markdown(
            f"""
    <style>
        .reportview-container .main .block-container{{
            max-width: {max_width}px;
            padding-top: {padding_top}rem;
            padding-right: {padding_right}rem;
            padding-left: {padding_left}rem;
            padding-bottom: {padding_bottom}rem;
        }}
        .reportview-container .main {{
            color: {COLOR};
            background-color: {BACKGROUND_COLOR};
        }}
    </style>
    """,
            unsafe_allow_html=True,
    )
    menu = ["News", "Analysis"]
    #st.sidebar.image('./img/LGES_ver00.jpg')
    choice = st.sidebar.radio("Menu", menu)

    s_date = st.sidebar.date_input('Start Date').strftime('%Y%m%d')
    e_date = st.sidebar.date_input('End Date').strftime('%Y%m%d')
    submit = st.sidebar.button("Search")


    st.markdown("<h1 style='text-align: center; color: black;'>News Summary Report</h1>", unsafe_allow_html=True)

    st.write( """
                ##
                """)


    #_, r1c2, r1c3, r1c4 = st.beta_columns((4,2,2,2))
    #r1c2.markdown("<h3 style='text-align: center; color: black;'>Date : </h3>", unsafe_allow_html=True)

    if submit:
        st.write( """
                    ##

                    """)

        conn = _call_db_info()
        read = conn.cursor()
        tmp_abstract_sql = "select * from abstract where date>='%s' and date <='%s'"%(s_date, e_date)
        tmp_content_sql = "select * from content where date>='%s' and date <='%s'"%(s_date, e_date)
        tmp_infer_sql = "select * from infer where date>='%s' and date <='%s'"%(s_date, e_date)
        read.execute(tmp_abstract_sql)
        tmp_abstract = pd.DataFrame(read.fetchall())
        read.execute(tmp_content_sql)
        tmp_content = pd.DataFrame(read.fetchall())
        read.execute(tmp_infer_sql)
        tmp_infer = pd.DataFrame(read.fetchall())
        read.close()

        abs_col = ['id', 'date', 'site', 'word', 'url', 'title']
        cont_col = ['id', 'date', 'site', 'word', 'content']
        infer_col = ['id', 'date', 'site', 'word', 'summary', 'label']




        if choice == 'News':
            if len(tmp_abstract) > 0:
                tmp_abstract.columns = list(abs_col)
                tmp_content.columns = list(cont_col)
                tmp_infer.columns = list(infer_col)
                tmp_rslt = pd.merge(pd.merge(tmp_abstract, tmp_content, how='inner', on=['id', 'date','site','word']), tmp_infer, how='inner', on=['id', 'date','site','word'])

                tmp1_ = tmp_rslt[tmp_rslt['label']=='0'].reset_index(drop=True)
                tmp2_ = tmp_rslt[tmp_rslt['label']=='1'].reset_index(drop=True)
                tmp3_ = tmp_rslt[tmp_rslt['label']=='2'].reset_index(drop=True)
                tmp4_ = tmp_rslt[tmp_rslt['label']=='3'].reset_index(drop=True)

                r2c1,r2c2 = st.beta_columns((2,2))
                with r2c1.beta_container():
                    r2c1.subheader("**자사**")

                    if len(tmp1_)<=5 and len(tmp1_)>=1:
                        for i in range(len(tmp1_)):
                            r2c1.markdown("**{}**".format(tmp1_.loc[i]['title']))
                            r2c1.markdown(tmp1_.loc[i]['summary'])
                            r2c1.markdown('-자세히 보기: {}'.format(tmp1_.loc[i]['url']), unsafe_allow_html=True)
                            r2c1.markdown("**********")
                    elif len(tmp1_)>5:
                        for i in range(5):
                            r2c1.markdown("**{}**".format(tmp1_.loc[i]['title']))
                            r2c1.markdown(tmp1_.loc[i]['summary'])
                            r2c1.markdown('-자세히 보기: {}'.format(tmp1_.loc[i]['url']), unsafe_allow_html=True)
                            r2c1.markdown("**********")

                    elif len(tmp1_) == 0:
                        r2c1.markdown('기사가 없습니다')
                    
            

                    # r2c1.markdown("<h2 style='text-align: center; color: black;'>자사</h2>", unsafe_allow_html=True)
                    # r2c1.write(tmp1_.to_html(escape=False, index=False), unsafe_allow_html=True)
                with r2c2.beta_container():
                    r2c2.subheader("**고객사**")
                    if len(tmp2_)<=5 and len(tmp2_)>=1:
                        for i in range(len(tmp2_)):
                            r2c2.markdown("**{}**".format(tmp2_.loc[i]['title']))
                            r2c2.markdown(tmp2_.loc[i]['summary'])
                            r2c2.markdown('-자세히 보기: {}'.format(tmp2_.loc[i]['url']), unsafe_allow_html=True)
                            r2c2.markdown("**********")
                    elif len(tmp2_)>5:
                        for i in range(5):
                            r2c2.markdown("**{}**".format(tmp2_.loc[i]['title']))
                            r2c2.markdown(tmp2_.loc[i]['summary'])
                            r2c2.markdown('-자세히 보기: {}'.format(tmp2_.loc[i]['url']), unsafe_allow_html=True)
                            r2c2.markdown("**********")
                    elif len(tmp2_) == 0:
                        r2c2.markdown('기사가 없습니다')

                
                st.write( """
                    ##
                    """)

                r3c1,r3c2 = st.beta_columns((2,2))

                with r3c1.beta_container():
                    r3c1.subheader("**경쟁사**")
                    if len(tmp3_)<=5 and len(tmp3_)>=1:
                        for i in range(len(tmp3_)):
                            r3c1.markdown("**{}**".format(tmp3_.loc[i]['title']))
                            r3c1.markdown(tmp3_.loc[i]['summary'])
                            r3c1.markdown('-자세히 보기: {}'.format(tmp3_.loc[i]['url']), unsafe_allow_html=True)
                            r3c1.markdown("**********")

                    elif len(tmp3_)>5:
                        for i in range(5):
                            r3c1.markdown("**{}**".format(tmp3_.loc[i]['title']))
                            r3c1.markdown(tmp3_.loc[i]['summary'])
                            r3c1.markdown('-자세히 보기: {}'.format(tmp3_.loc[i]['url']), unsafe_allow_html=True)
                            r3c1.markdown("**********")
                    elif len(tmp3_) == 0:
                        r3c1.markdown('기사가 없습니다')

                with r3c2.beta_container():
                    r3c2.subheader("**산업/기술 동향**")
                    if len(tmp4_)<=5 and len(tmp4_)>=1:
                        for i in range(len(tmp4_)):
                            r3c2.markdown("**{}**".format(tmp4_.loc[i]['title']))
                            r3c2.markdown(tmp4_.loc[i]['summary'])
                            r3c2.markdown('-자세히 보기: {}'.format(tmp4_.loc[i]['url']), unsafe_allow_html=True)
                            r3c2.markdown("**********")
                    elif len(tmp4_)>5:
                        for i in range(5):
                            r3c2.markdown("**{}**".format(tmp4_.loc[i]['title']))
                            r3c2.markdown(tmp4_.loc[i]['summary'])
                            r3c2.markdown('-자세히 보기: {}'.format(tmp4_.loc[i]['url']), unsafe_allow_html=True)
                            r3c2.markdown("**********")
                    elif len(tmp4_) == 0:
                        r3c2.markdown('기사가 없습니다')
                
            elif len(tmp_abstract) == 0:
                st.subheader("기사가 없습니다")

        if choice == 'Analysis':
            with st.beta_container():
                tmp_abstract.columns = list(abs_col)
                tmp_content.columns = list(cont_col)
                tmp_infer.columns = list(infer_col)
                tmp_rslt = pd.merge(pd.merge(tmp_abstract, tmp_content, how='inner', on=['id', 'date','site','word']), tmp_infer, how='inner', on=['id', 'date','site','word'])
                
                if len(tmp_abstract) > 0:           
                
                    tmp1_ = tmp_rslt[tmp_rslt['label']=='0'].reset_index(drop=True)
                    tmp2_ = tmp_rslt[tmp_rslt['label']=='1'].reset_index(drop=True)
                    tmp3_ = tmp_rslt[tmp_rslt['label']=='2'].reset_index(drop=True)
                    tmp4_ = tmp_rslt[tmp_rslt['label']=='3'].reset_index(drop=True)
                                
                    cnt_article = tmp_rslt.groupby(['date','label']).count()[['title']]
                    cnt_article = cnt_article.reset_index()
                    
                    #cnt_article = tmp_rslt.groupby(['label']).count()[['title']]
                    #cnt_article['분류'] = cnt_article.index
                    #cnt_article['분류']=cnt_article['분류'].replace({'0':'자사', '1':'고객사', '2':'경쟁사', '3':'산업/기술 동향'})
                    #cnt_article['기사개수'] = cnt_article['title']
                    
                    st.subheader('**기사 개수 통계**')
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=cnt_article[cnt_article['label']=='0'].date, y=cnt_article[cnt_article['label']=='0'].title, name='자사'))
                    fig.add_trace(go.Bar(x=cnt_article[cnt_article['label']=='1'].date, y=cnt_article[cnt_article['label']=='1'].title, name='고객사'))
                    fig.add_trace(go.Bar(x=cnt_article[cnt_article['label']=='2'].date, y=cnt_article[cnt_article['label']=='2'].title, name='경쟁사'))
                    fig.add_trace(go.Bar(x=cnt_article[cnt_article['label']=='3'].date, y=cnt_article[cnt_article['label']=='3'].title, name='산업/기술'))

                    #fig.add_trace(go.Bar(x=[cnt_article['분류'].tolist()],y=[cnt_article['기사개수'].tolist()]))
                    st.plotly_chart(fig, use_container_width=True)
                    # fig = go.Figure([go.Bar(x=[cnt_article['분류'].tolist()], y=[cnt_article['기사개수'].tolist()])])
                    # fig = go.Figure([go.Bar(x=[['자사', '고객사']], y=[[3,10]])])
                    # st.plotly_chart(fig, use_container_width=True)
                    #st.table(cnt_article[['분류', '기사개수']])     

            with st.beta_container():
                node_tr, edge_tr =  draw_networkx(tmp_content)
                layout = go.Layout(
                    paper_bgcolor='#EEEEEE', # transparent background
                    plot_bgcolor='#DDDDDD', # transparent 2nd background
                    xaxis =  {'showgrid': False, 'zeroline': False}, # no gridlines
                    yaxis = {'showgrid': False, 'zeroline': False}, # no gridlines
                )

                fig_n = go.Figure(layout=layout)
                for trace in edge_tr:
                    fig_n.add_trace(trace)
                fig_n.add_trace(node_tr)
                fig_n.update_layout(showlegend=False)
                st.plotly_chart(fig_n, use_container_width=True)



        elif len(tmp_abstract) ==0:
            st.subheader("기사가 없습니다")


session_state = get(password='')

conn = _call_db_info()
chk_user = conn.cursor()
user_sql = "select pwd from user_info where id = 'user1'"
chk_user.execute(user_sql)
pwd_info = pd.DataFrame(chk_user.fetchall())
chk_user.close()
#s_date = st.sidebar.date_input('Start Date').strftime('%Y%m%d')
#e_date = st.sidebar.date_input('End Date').strftime('%Y%m%d')
#submit = st.sidebar.button("Search")

if session_state.password != pwd_info.values:
    pwd_placeholder = st.empty()
    pwd = pwd_placeholder.text_input('Password : ', value='', type='password')
    session_state.password = pwd
    if session_state.password == pwd_info.values:
        pwd_placeholder.empty()
        main()
    elif session_state.password == '':
        st.text("시스템을 이용하시려면 패스워듣 입력해주세요.")
    else:
        st.error("올바른 패스워드가 아닙니다. 다시 입력해주세요.")
else:
    main()