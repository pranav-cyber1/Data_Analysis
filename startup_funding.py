import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

df=pd.read_csv("/home/codex/Desktop/Python/streamlit_app/startup_funding.csv")
#st.dataframe(df)

# Data cleaning part
df.rename(columns={
    "Sr No":"sr_no",
    "Date dd/mm/yyyy":"date",
    "Startup Name":"startups",
    "Industry Vertical":"vertical",
    "SubVertical":"subvertical",
    "City  Location":"city",
    "Investors Name":"investors",
    "InvestmentnType":"round",
    "Amount in USD":"amount"
},inplace=True)

df.drop(columns="Remarks",inplace=True)
df.set_index("sr_no",inplace=True)
df["amount"]=df["amount"].fillna("0")
df["amount"]=df["amount"].str.replace(",",'')
df["amount"]=df["amount"].str.replace("undisclosed",'0')
df["amount"]=df["amount"].str.replace("unknown",'0')
df["amount"]=df["amount"].str.replace("Undisclosed",'')
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["amount"] = df["amount"].fillna(0)


#convert to date_time format
df["date"]=df["date"].str.replace("05/072018","05/07/2018")
df["date"]=pd.to_datetime(df["date"],errors="coerce")
df["month"]=df["date"].dt.month
df["year"]=df["date"].dt.year
#changing column names
df=df.dropna(subset=["date","startups","vertical","city","investors","round","amount"])


#function to convert from USD to INR
def to_inr(dollar):
    inrupee=dollar*96.10
    return inrupee/10000000
df["amount"]=df["amount"].apply(to_inr)

#function to find investor detail
def load_investor_detail(investor):
    st.title(investor+" "+"Dashboard")
    #load the recent five investment
    last5_df=df[df["investors"].str.contains(investor)].head()[["date","startups","vertical","city","round","amount"]]
    st.subheader("Last five investments")
    st.dataframe(last5_df)


#function maximum money invested by a invester in a particular startups
def max_invest(investor):
    col1,col2=st.columns(2)

    with col1:
        amounts_series=df[df["investors"].str.contains(investor)].groupby("startups")["amount"].sum().sort_values(ascending=False).head()
        st.subheader("Biggest  five Investment")
        fig,ax=plt.subplots()
        ax.bar(amounts_series.index,amounts_series.values)
        plt.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
    with col2:
        domain_invest=df[df["investors"].str.contains(investor)].groupby("vertical")["amount"].sum()
        st.subheader("Investment in each sector")
        fig1,ax1=plt.subplots()
        ax1.pie(domain_invest,labels=domain_invest.index,autopct="%0.01f%%")
        st.pyplot(fig1)

#stage
def stage(investor):
    stage_series=df[df["investors"].str.contains(investor)].groupby("round")["amount"].sum()
    col1,col2=st.columns(2)
    with col1:
        st.subheader("Investment in each stage")
        fig2,ax2=plt.subplots()
        ax2.pie(stage_series,labels=stage_series.index,autopct="%0.01f%%")
        st.pyplot(fig2)
    with col2:
        city_series=df[df["investors"].str.contains(investor)].groupby("city")["amount"].sum()   
        st.subheader("Investment in each city")
        fig3,ax3=plt.subplots()
        ax3.pie(city_series,labels=city_series.index,autopct="%0.01f%%")
        st.pyplot(fig3)

#Year_on_Year Investments by the particular company
def YOY(investor):
    col1,col2=st.columns(2)
    with col1:
        #df["year"]=df["date"].dt.year
        df1=df[df["investors"].str.contains(investor)].groupby("year")["amount"].sum()
        st.subheader("Year on Year Investments")
        fig4,ax4=plt.subplots()
        ax4.plot(df1.index,df1.values)
        ax4.set_xlabel("Year")
        ax4.set_ylabel("Investment Amount in Crore")
        st.pyplot(fig4)

#General Analysis
def general_analysis():
    st.title("Overall Analysis")
    col1,col2,col3,col4=st.columns(4)
    #total invested amount
    with col1:
        total=round(df["amount"].sum())
        st.metric("Total",str(total)+"Cr")
    #Maximum Funding  
    with col2:    
        max_funding=df.groupby("startups")["amount"].max().sort_values(ascending=False).head(1).values[0]
        st.metric("Max",str(round(max_funding))+"Cr")
    #Average Funding
    with col3:
        avg=df.groupby("startups")["amount"].sum().mean()
        st.metric("Average Funding",str(round(avg))+"Cr")
    with col4:
        total_funded_startup=df["startups"].nunique()
        st.metric("Total Funded Startups",total_funded_startup)

    #Amalysis on the basis of month
    st.header('MoM graph')
    listx=['Total','Count']
    selected_option = st.selectbox('Select Type',listx)
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
        temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')
        fig3, ax3 = plt.subplots()
        ax3.plot(temp_df['x_axis'], temp_df['amount'])
        st.pyplot(fig3)
    elif selected_option=='Count':
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()
        temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')
        fig3, ax3 = plt.subplots()
        ax3.plot(temp_df['x_axis'], temp_df['amount'])
        st.pyplot(fig3)

    

st.set_page_config(layout="wide",page_title="startup_analysis")
st.sidebar.title("STARTUP FUNDING ANALYSIS")

option=st.sidebar.selectbox("Select One",["Overall Analysis","StartUp","Investor"])

list1=sorted(df["startups"].unique().tolist())
list2=sorted(set(df["investors"].str.split(",").sum()))

if option=="Overall Analysis":
    btn1=st.sidebar.button("Show Overall analysis")
    if btn1:
        general_analysis()
elif option=="StartUp":
    st.sidebar.selectbox("Select StartUp",list1)
    btn2=st.sidebar.button("Find StartUp Details")
    st.title("StartUp Analysis")
else:
    selected_investor=st.sidebar.selectbox("Select Investor",list2)
    btn3=st.sidebar.button("Find Investor Details")
    if btn3:
        load_investor_detail(selected_investor)
        max_invest(selected_investor)
        stage(selected_investor)
        YOY(selected_investor)
    
