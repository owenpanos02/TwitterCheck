from flask import Flask, render_template, request, redirect
import os
app = Flask(__name__)
picFolder = os.path.join('static', 'pictures')
app.config['UPLOAD_FOLDER'] = picFolder


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        import tweepy
        import pandas as pd
        from textblob import TextBlob
        import requests
        import matplotlib.pyplot as plt

# Retrieve below from twitter dev account      
        api_key = {ENTER API KEY HERE}
        api_secret_key = {ENTER API SECRET KEY}
        bearer_token = {ENTER BEARER TOKEN}
        access_token = {ENTER ACCESS TOKEN}
        access_token_secret = {ENTER SECRET ACCESS TOKEN}

        client = tweepy.Client(bearer_token = bearer_token,
                                consumer_key= api_key,
                                consumer_secret= api_secret_key,
                                access_token= access_token,
                                access_token_secret = access_token_secret,
                                return_type = requests.Response,
                                wait_on_rate_limit= True
                                )



        query = request.form['topic']

        tweets = client.search_recent_tweets(query = query + ' -is: retweet',
                                                tweet_fields = ['author_id','created_at'],
                                                max_results=50)

        tweets_dict = tweets.json()

        tweet_data = tweets_dict['data']

        df = pd.json_normalize(tweet_data)

        df['polarity'] = df['text'].apply(lambda x: float(TextBlob(x).sentiment.polarity))
        df['subjectivity'] = df['text'].apply(lambda x: float(TextBlob(x).sentiment.subjectivity))
        df.loc[:, 'sentiment'] = 'nt'
        df.loc[df['polarity'] > 0.3, 'sentiment']= 'pos'
        df.loc[df['polarity'] < -0.3, 'sentiment']= 'neg'

        recent_50 = df.head(50)
        pos_total = 0
        nt_total = 0 
        neg_total = 0
        sentiments = []
        for i in df['sentiment']:
            sentiments.append(i)
            if i == 'pos':
                pos_total += 1
            elif i == 'nt':
                nt_total += 1
            else:
                neg_total += 1

        total = pos_total + nt_total + neg_total

        print(f"Pos: {pos_total / total * 100:.2f}%\nNt: {nt_total / total * 100:.2f}%\nNeg: {neg_total / total * 100:.2f}")


        labels = ['Positive', 'Neutral', 'Negative']
        colors = ['#99ff66', '#ffcc00', '#ff0000']
        sentiment_df = pd.DataFrame({'percentage': [pos_total, nt_total, neg_total]}, index=labels)
        fig, ax1 = plt.subplots()
        ax1.pie(sentiment_df['percentage'], explode=None, labels=labels,colors=colors, autopct='%1.1f%%')
        

        os.remove("static\pictures\plot.png")
        fig.savefig('static\pictures\plot.png', transparent=True)

        pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'plot.png')

      


        return(render_template('index.html', value = query, user_image = pic1))
    
    else:
        return(render_template('index.html'))


if __name__ == '__main__':
    app.run()
