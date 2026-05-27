import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import io

st.sidebar.title("Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:

    raw_bytes = uploaded_file.getvalue()

    # Detect ZIP by magic bytes b'PK' instead of filename
    # (Streamlit can alter filenames, so checking file header is more reliable)
    if raw_bytes[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
            txt_files = [f for f in z.namelist() if f.endswith(".txt")]
            if not txt_files:
                st.error("No .txt file found inside the ZIP.")
                st.stop()
            with z.open(txt_files[0]) as f:
                bytes_data = f.read()
    else:
        bytes_data = raw_bytes

    # Decode with UTF-8, fallback to latin-1
    try:
        data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        data = bytes_data.decode("latin-1")

    df = preprocessor.preprocess(data)
    st.dataframe(df)

    # fetch unique users
    user_list = df["user"].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analyze"):

        # stats arena
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)

        with col2:
            st.header("Total Words")
            st.title(words)

        with col3:
            st.header("Total Media Messages")
            st.title(num_media_messages)

        with col4:
            st.header("Total Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline["message"], color="lightgreen")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline["message"], color="black")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.monthly_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # weekly activity heatmap
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        if not user_heatmap.empty and user_heatmap.values.sum() > 0:
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
        else:
            st.info("Not enough data to display heatmap.")

        # most busy users (group level only)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='lightblue')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # wordcloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc is not None:
            fig, ax = plt.subplots()
            plt.imshow(df_wc)
            plt.axis('off')
            st.pyplot(fig)
        else:
            st.info("Not enough text to generate a word cloud.")

        # most common words
        most_common_df = helper.most_common_words(selected_user, df)
        if most_common_df is not None:
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1], color='lightgreen')
            plt.xticks(rotation='vertical')
            st.title("Most Common Words")
            st.pyplot(fig)
        else:
            st.title("Most Common Words")
            st.info("Not enough data to display common words.")

        # emoji analysis
        st.title("Emojis Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        if emoji_df is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%1.1f%%")
                st.pyplot(fig)
        else:
            st.info("No emojis found.")