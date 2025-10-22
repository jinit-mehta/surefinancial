import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api"

# Page config
st.set_page_config(
    page_title="Credit Card Statement Parser",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        color: #721c24;
    }
    .info-card {
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
        color: white;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">💳 Credit Card Statement Parser</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/bank-card-back-side.png", width=80)
        st.title("Navigation")
        page = st.radio("Go to", ["📤 Upload Statement", "📊 Dashboard", "📈 Analytics", "ℹ️ About"])
        
        st.markdown("---")
        st.markdown("### Supported Banks")
        st.markdown("✅ HDFC Bank")
        st.markdown("✅ ICICI Bank")
        st.markdown("✅ SBI Card")
        st.markdown("✅ Axis Bank")
        st.markdown("✅ American Express")
    
    # Main content
    if page == "📤 Upload Statement":
        upload_page()
    elif page == "📊 Dashboard":
        dashboard_page()
    elif page == "📈 Analytics":
        analytics_page()
    else:
        about_page()

def upload_page():
    st.header("📤 Upload Credit Card Statement")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Instructions:**
        1. Upload your credit card statement PDF
        2. System will automatically detect the bank
        3. View extracted information instantly
        4. Download results as CSV
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload credit card statement from HDFC, ICICI, SBI, Axis, or AMEX"
        )
        
        if uploaded_file is not None:
            if st.button("🔍 Parse Statement", type="primary"):
                with st.spinner("Processing PDF... This may take a few seconds"):
                    try:
                        # Send to API
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                        response = requests.post(f"{API_URL}/upload", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            data = result.get("data", {})
                            
                            st.markdown('<div class="success-box">✅ Statement parsed successfully!</div>', unsafe_allow_html=True)
                            st.balloons()
                            
                            # Display results
                            st.markdown("### 📋 Extracted Information")
                            
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                st.metric("🏦 Bank", data.get("bank_name", "N/A"))
                                st.metric("💳 Card Variant", data.get("card_variant", "N/A"))
                            
                            with col_b:
                                st.metric("🔢 Last 4 Digits", data.get("last_4_digits", "N/A"))
                                st.metric("📅 Due Date", data.get("due_date", "N/A"))
                            
                            with col_c:
                                amount = data.get("total_amount_due", 0)
                                st.metric("💰 Total Due", f"₹{amount:,.2f}")
                                st.metric("📆 Billing Cycle", data.get("billing_cycle", "N/A"))
                            
                            # Download button
                            if st.button("📥 Download as CSV"):
                                stmt_id = data.get("id")
                                if stmt_id:
                                    csv_response = requests.get(f"{API_URL}/export/{stmt_id}")
                                    st.download_button(
                                        label="💾 Save CSV File",
                                        data=csv_response.content,
                                        file_name=f"statement_{stmt_id}.csv",
                                        mime="text/csv"
                                    )
                        
                        else:
                            error_msg = response.json().get("detail", "Unknown error")
                            st.markdown(f'<div class="error-box">❌ Error: {error_msg}</div>', unsafe_allow_html=True)
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API server. Please ensure the backend is running on http://localhost:8000")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.info("""
        **Supported Formats:**
        - PDF only
        - Text-based PDFs
        - Official bank statements
        
        **What we extract:**
        - Bank name
        - Card variant
        - Last 4 digits
        - Billing cycle
        - Payment due date
        - Total amount due
        """)

def dashboard_page():
    st.header("📊 Statement Dashboard")
    
    try:
        # Fetch history
        response = requests.get(f"{API_URL}/history?limit=100")
        
        if response.status_code == 200:
            result = response.json()
            statements = result.get("data", [])
            
            if not statements:
                st.info("No statements uploaded yet. Go to the Upload page to get started!")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(statements)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📄 Total Statements", len(df))
            
            with col2:
                total_due = df['total_amount_due'].sum()
                st.metric("💰 Total Due", f"₹{total_due:,.2f}")
            
            with col3:
                unique_banks = df['bank_name'].nunique()
                st.metric("🏦 Banks", unique_banks)
            
            with col4:
                avg_due = df['total_amount_due'].mean()
                st.metric("📊 Avg Due", f"₹{avg_due:,.2f}")
            
            st.markdown("---")
            
            # Data table
            st.subheader("📑 Recent Statements")
            
            # Format DataFrame for display
            display_df = df[[
                'id', 'bank_name', 'card_variant', 'last_4_digits',
                'due_date', 'total_amount_due', 'upload_timestamp'
            ]].copy()
            
            display_df.columns = [
                'ID', 'Bank', 'Card Type', 'Last 4',
                'Due Date', 'Amount Due (₹)', 'Uploaded'
            ]
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Download all button
            if st.button("📥 Export All to CSV"):
                csv_response = requests.get(f"{API_URL}/export/all")
                st.download_button(
                    label="💾 Save All Statements CSV",
                    data=csv_response.content,
                    file_name="all_statements.csv",
                    mime="text/csv"
                )
        
        else:
            st.error("Failed to fetch data from API")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure the backend is running.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def analytics_page():
    st.header("📈 Analytics & Insights")
    
    try:
        # Fetch stats
        response = requests.get(f"{API_URL}/stats")
        history_response = requests.get(f"{API_URL}/history?limit=100")
        
        if response.status_code == 200 and history_response.status_code == 200:
            stats = response.json().get("data", {})
            statements = history_response.json().get("data", [])
            
            if not statements:
                st.info("No data available for analytics yet.")
                return
            
            df = pd.DataFrame(statements)
            
            # Bank-wise breakdown
            st.subheader("🏦 Bank-wise Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                bank_counts = df['bank_name'].value_counts()
                fig_pie = px.pie(
                    values=bank_counts.values,
                    names=bank_counts.index,
                    title="Distribution by Bank",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart
                bank_due = df.groupby('bank_name')['total_amount_due'].sum().sort_values(ascending=False)
                fig_bar = px.bar(
                    x=bank_due.index,
                    y=bank_due.values,
                    title="Total Amount Due by Bank",
                    labels={'x': 'Bank', 'y': 'Total Due (₹)'},
                    color=bank_due.values,
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Timeline
            st.subheader("📅 Upload Timeline")
            
            df['upload_date'] = pd.to_datetime(df['upload_timestamp']).dt.date
            timeline = df.groupby('upload_date').size().reset_index(name='count')
            
            fig_timeline = px.line(
                timeline,
                x='upload_date',
                y='count',
                title="Statements Uploaded Over Time",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Top cards by amount
            st.subheader("💳 Top Cards by Amount Due")
            top_cards = df.nlargest(5, 'total_amount_due')[[
                'bank_name', 'card_variant', 'last_4_digits', 'total_amount_due'
            ]]
            st.table(top_cards)
        
        else:
            st.error("Failed to fetch analytics data")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def about_page():
    st.header("ℹ️ About This Project")
    
    st.markdown("""
    ### Credit Card Statement Parser MVP
    
    **Version:** 1.0.0  
    **Tech Stack:**
    - **Backend:** FastAPI (Python 3.10+)
    - **Frontend:** Streamlit
    - **PDF Parsing:** pdfplumber & PyMuPDF
    - **Database:** SQLite
    
    ---
    
    #### 🎯 Features
    - ✅ Upload PDF credit card statements
    - ✅ Automatic bank detection (HDFC, ICICI, SBI, Axis, AMEX)
    - ✅ Extract key information using regex patterns
    - ✅ Store parsed data in SQLite database
    - ✅ View dashboard with all statements
    - ✅ Analytics and insights
    - ✅ Export to CSV
    - ✅ RESTful API for programmatic access
    
    ---
    
    #### 🚀 Quick Start
    
    **1. Start Backend:**
```bash
    cd backend
    uvicorn main:app --reload
```
    
    **2. Start Frontend:**
```bash
    cd frontend
    streamlit run streamlit_app.py
```
    
    ---
    
    #### 📚 API Endpoints
    - `POST /api/upload` - Upload and parse statement
    - `GET /api/history` - Get all statements
    - `GET /api/statement/{id}` - Get specific statement
    - `GET /api/export/{id}` - Export statement as CSV
    - `GET /api/stats` - Get analytics
    
    ---
    
    #### 🔒 Privacy & Security
    - All data stored locally
    - No cloud uploads
    - SQLite database for quick access
    - Files deleted after processing
    
    ---
    
    #### 👨‍💻 Developer Info
    Built as a production-ready MVP for credit card statement parsing and analysis.
    """)
    
    st.success("✨ Ready for internship demonstration!")

if __name__ == "__main__":
    main()