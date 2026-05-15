import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import zipfile
import io
import datetime

st.set_page_config(
    page_title='Afficionado Coffee Executive Dashboard',
    page_icon='☕',
    layout='wide'
)

st.title('☕ Afficionado Coffee Executive Analytics Dashboard')
st.caption('Senior Analyst Edition: Product, Revenue, Time & Store Intelligence')

@st.cache_data
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df=pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            df=pd.read_excel(file)
        elif file.name.endswith('.zip'):
            with zipfile.ZipFile(file) as z:
                for f in z.namelist():
                    if f.endswith('.csv'):
                        with z.open(f) as x:
                            df=pd.read_csv(x)
                            break
                    elif f.endswith('.xlsx'):
                        with z.open(f) as x:
                            df=pd.read_excel(io.BytesIO(x.read()))
                            break
        else:
            st.error('Unsupported file')
            st.stop()

        for col in df.columns:
            if df[col].dtype=='object':
                sample=df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if isinstance(sample,datetime.time):
                    df[col]=df[col].astype(str)

        time_data=pd.to_datetime(df['transaction_time'],errors='coerce')

        df['Revenue']=df['transaction_qty']*df['unit_price']
        df['Hour']=time_data.dt.hour
        df['Date']=time_data.dt.date
        df['Month']=time_data.dt.month_name()
        df['Day']=time_data.dt.day_name()
        df['Minute']=time_data.dt.minute
        df['Time']=time_data.dt.strftime('%H:%M:%S')
        df['AM_PM']=time_data.dt.strftime('%p')

        df['Time_Period']=pd.cut(
            df['Hour'],
            bins=[0,6,12,17,21,24],
            labels=['Night','Morning','Afternoon','Evening','Late Night'],
            include_lowest=True
        )
        return df
    except Exception as e:
        st.error(f'Error processing file: {e}')
        st.stop()

uploaded=st.sidebar.file_uploader('Upload file',type=['csv','xlsx','zip'])
if uploaded is None:
    st.info('Upload your coffee dataset')
    st.stop()

df=load_data(uploaded)

st.sidebar.header('Filters')
cat=st.sidebar.multiselect('Category',df.product_category.unique(),default=df.product_category.unique())
store=st.sidebar.multiselect('Store',df.store_location.unique(),default=df.store_location.unique())
ptype=st.sidebar.multiselect('Product Type',df.product_type.unique(),default=df.product_type.unique())

f=df[(df.product_category.isin(cat))&(df.store_location.isin(store))&(df.product_type.isin(ptype))]

rev=f['Revenue'].sum()
sales=f['transaction_qty'].sum()
products=f['product_id'].nunique()
avg=f['unit_price'].mean()
peak=f.groupby('Hour')['Revenue'].sum().idxmax()

c1,c2,c3,c4,c5=st.columns(5)
c1.metric('Revenue',f'${rev:,.0f}')
c2.metric('Sales',f'{sales:,.0f}')
c3.metric('Products',products)
c4.metric('Avg Price',f'${avg:.2f}')
c5.metric('Peak Hour',f'{peak}:00')

col1,col2=st.columns(2)
with col1:
    x=f.groupby('product_category')['Revenue'].sum().reset_index()
    st.plotly_chart(px.pie(x,names='product_category',values='Revenue',hole=.5,title='Revenue Share'),use_container_width=True)
with col2:
    h=f.groupby('Hour')['Revenue'].sum().reset_index()
    st.plotly_chart(px.line(h,x='Hour',y='Revenue',markers=True,title='Hourly Revenue Trend'),use_container_width=True)

col3,col4=st.columns(2)
with col3:
    top=f.groupby('product_detail')['Revenue'].sum().sort_values(ascending=False).head(10).reset_index()
    st.plotly_chart(px.bar(top,x='product_detail',y='Revenue',color='Revenue',title='Top Products'),use_container_width=True)
with col4:
    scat=f.groupby('product_detail').agg({'transaction_qty':'sum','Revenue':'sum'}).reset_index()
    st.plotly_chart(px.scatter(scat,x='transaction_qty',y='Revenue',size='Revenue',hover_name='product_detail',title='Popularity vs Revenue'),use_container_width=True)

st.subheader('Pareto Analysis')
p=f.groupby('product_detail')['Revenue'].sum().sort_values(ascending=False).reset_index()
p['cum']=p['Revenue'].cumsum()/p['Revenue'].sum()*100
fig=make_subplots(specs=[[{'secondary_y':True}]])
fig.add_bar(x=p['product_detail'],y=p['Revenue'])
fig.add_scatter(x=p['product_detail'],y=p['cum'],secondary_y=True)
st.plotly_chart(fig,use_container_width=True)

st.subheader('Store vs Category Heatmap')
heat=f.pivot_table(values='Revenue',index='store_location',columns='product_category',aggfunc='sum')
st.plotly_chart(px.imshow(heat,text_auto=True),use_container_width=True)

st.subheader('Business Insights')
st.success(f'Top Product: {top.iloc[0]["product_detail"]}')
st.info(f'Peak Revenue Hour: {peak}:00')
st.warning('Use top-performing products for promotion and inventory prioritization.')

st.dataframe(f,use_container_width=True)
