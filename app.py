from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from pathlib import Path
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import ast
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD

app = Flask(__name__,template_folder='templates',static_folder='static')

event_score={'view':1, 'saved_for_later':3, 'added_to_cart':4, 'bought':15, 'like':2}
sub_categories_all=[ 'accessories', 'baby_clothing', 'baby_gear', 'bakery', 'bath_and_body', 'bedroom', 'beverages', 'cameras', 'children_clothing', 'climate_control', 'dairy_and_eggs', 'diapers', 'dining_room', 'entertainment', 'feeding_essentials', 'feminine_care', 'first_aid', 'fitness_equipment', 'footwear', 'fragrances', 'fresh_products', 'frozen_foods', 'gaming', 'haircare', 'headphones', 'healthy_snacks', 'health_and_safety', 'home_cleaning', 'home_decor', 'hygiene', 'jewelry', 'kids', 'kitchen_appliances', 'laptops', 'laundry', 'living_room', 'maternity_and_pregnancy', 'meat_and_sea_food', 'medical_supplies', 'mens_clothing', 'mens_grooming', 'mobiles', 'nursery_and_bedding', 'office', 'oral_care', 'outdoor', 'outerwear', 'pantry', 'personal_care', 'personal_care_products', 'personal_hygiene', 'skincare', 'small_kitchen', 'smart_home', 'snacks', 'sports', 'sportswear', 'storage', 'styling', 'televisions','toys_and_games', 'vitamins_and_supplements', 'watches', 'womens_clothing']
user_id=''
category=""
sub_category_index=0
cat_sub={
    'Electronics':[['Mobiles','Laptops','Watches','Styling devices','Cameras','Gaming','Televisions','Headphones'],
                   ['mobiles.jpg','laptops.jpg','watches.jpg','styling.jpg','cameras.jpg','gaming.jpg','televisions.jpg','headphones.jpg']],

    'Grocery':[[
    "Fresh Produce",
    "Dairy and Eggs",
    "Bakery",
    "Meat and Seafood",
    "Pantry Staples",
    "Frozen Foods",
    "Beverages",
    "Snacks"
],['fresh_products.jpg','dairy_and_eggs.jpg','bakery.jpg','meat_and_sea_food.jpg','pantry.jpg','frozen_foods.jpg','beverages.jpg','snacks.jpg']],
    
    'Fashion':[[
    "Men's Clothing",
    "Women's Clothing",
    "Footwear",
    "Accessories",
    "Jewelry",
    "Sportswear",
    "Children's Clothing",
    "Outerwear"
],['mens_clothing.jpg','womens_clothing.jpg','footwear.jpg','accessories.jpg','jewelry.jpg','sportswear.jpg','children_clothing.jpg','outerwear.jpg']],
    
    'Furniture':[[
    "Living Room Furniture",
    "Bedroom Furniture",
    "Dining Room Furniture",
    "Office Furniture",
    "Outdoor Furniture",
    "Kids' Furniture",
    "Storage and Organization",
    "Home Decor"
],['living_room.jpg','bedroom.jpg','dining_room.jpg','office.jpg','outdoor.jpg','kids.jpg','storage.jpg','home_decor.jpg']],
    
    'Appliances':[[
    "Kitchen Appliances",
    "Home Cleaning Appliances",
    "Laundry Appliances",
    "Climate Control Appliances",
    "Personal Care Appliances",
    "Entertainment Appliances",
    "Smart Home Appliances",
    "Small Kitchen Gadgets"
],['kitchen_appliances.jpg','home_cleaning.jpg','laundry.jpg','climate_control.jpg','personal_care.jpg','entertainment.jpg','smart_home.jpg','small_kitchen.jpg']],
    
    'Nutrition & health': [[
    "Vitamins and Supplements",
    "Healthy Snacks",
    "Sports Nutrition",
    "Medical Supplies",
    "Personal Care Products",
    "Fitness Equipment",
    "First Aid and Health Aids",
    "Hygiene Products"
],['vitamins_and_supplements.jpg','healthy_snacks.jpg','sports.jpg','medical_supplies.jpg','personal_care_products.jpg','fitness_equipment.jpg','first_aid.jpg','hygiene.jpg']],
    
    'Personal Care':[[
    "Skincare",
    "Haircare",
    "Bath and Body",
    "Oral Care",
    "Fragrances",
    "Men's Grooming",
    "Feminine Care",
    "Personal Hygiene"
],['skincare.jpg','haircare.jpg','bath_and_body.jpg','oral_care.jpg','fragrances.jpg','mens_grooming.jpg','feminine_care.jpg','personal_hygiene.jpg']],
    
    'Toys & Baby':[[
    "Toys and Games",
    "Baby Gear and Furniture",
    "Baby Clothing and Accessories",
    "Diapers and Wipes",
    "Feeding Essentials",
    "Health and Safety",
    "Nursery and Bedding",
    "Maternity and Pregnancy"
],['toys_and_games.jpg','baby_gear.jpg','baby_clothing.jpg','diapers.jpg','feeding_essentials.jpg','health_and_safety.jpg','nursery_and_bedding.jpg','maternity_and_pregnancy.jpg']]
}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/send_users_to_web',methods=['POST'])
def send_users_to_web():
    udf=pd.read_csv('udf.csv',index_col=0)
    l=list(udf.index)
    return l

@app.route('/send_user',methods=['POST'])
def send_user():
    global user_id
    # print(request.form)
    udf=pd.read_csv('udf.csv',index_col=0)
    existing_users=list(udf.index)
    current_user=request.form.get('user_id')
    user_id=current_user
    # print(user_id)
    if current_user in existing_users:
        pass_key=udf.loc[user_id, 'password']
        if(str(pass_key) == request.form.get('password')):
            return "validated"
        return "not validated"
    else:
        new_name = request.form.get('new_name')
        new_password = request.form.get("new_password")
        new_confirmPassword = request.form.get("new_confirmPassword")
        new_number =request.form.get("new_number")
        new_user = {
            'password' :new_password,
            'name' : new_name,
            'complaints' : {x:{} for x in sub_categories_all}
        }
        udf.loc[current_user]= new_user
        print(udf.loc[current_user])
        udf.to_csv('udf.csv')
        return "good"
    

@app.route('/get_home')
def get_home():
    return render_template('home.html')

@app.route('/send_category',methods=['POST'])
def send_category():
    global category
    # print(request.form)
    category=request.form.get('q')
    # print(category) # getting category as none handle it
    return "hello"

@app.route('/send_sub_categories_to_web',methods=['POST'])
def send_sub_categories_to_web():
    global category
    # return "hello"
    l=cat_sub[category]
    return l

@app.route('/get_sub')
def get_sub():
    return render_template('sub.html')


@app.route('/send_sub_category',methods=['POST'])
def send_sub_category():
    global sub_category_index
    sub_category_index=int(request.form.get('q'))
    # print(sub_category)
    return "hello"

@app.route('/get_complaint')
def get_complaint():
    return render_template('complaint.html')

@app.route('/send_complaints_to_web',methods=['POST'])
def send_complaints_to_web():
    global user_id
    udf=pd.read_csv('udf.csv',index_col=0)
    udf['complaints']=udf['complaints'].apply(ast.literal_eval)
    p=udf.loc[user_id,'complaints']
    print(type(p))
    return p

@app.route('/send_orders_to_web',methods=['POST'])
def send_orders_to_web():
    global user_id
    orders={}
    for x in sub_categories_all:
        udf=pd.read_csv(x+'/udf.csv',index_col=0)
        udf['bought']=udf['bought'].apply(ast.literal_eval)
        if(user_id in udf.index):
            orders[x]=udf.loc[user_id,'bought']
    return orders

@app.route('/send_product_details_to_web',methods=['POST'])
def send_product_details_to_web():
    global user_id
    x = request.form.get('sub_cat')
    y = request.form.get('prod_id')
    pdf=pd.read_csv(x+'/pdf.csv',index_col=0)
    # print(type(pdf.loc[y].to_dict()))
    # return "hello"
    return pdf.loc[y].to_dict()

@app.route('/send_message_and_receive_response',methods=['POST'])
def send_message_and_receive_response():
    complaint = request.form.get("msg")
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(complaint)
    global user_id
    udf=pd.read_csv('udf.csv',index_col=0)
    udf['complaints']=udf['complaints'].apply(ast.literal_eval)
    response=""
    if scores['compound'] > 0.05:
        response="Low"
    elif scores['compound'] < -0.05:
        response="Highest"
    else:
        response="Medium"
    sub_cat = request.form.get("sub_cat")
    prod_id = request.form.get("prod_id")
    udf.loc[user_id,'complaints'][sub_cat][prod_id]=response
    # print(user_id)
    # print(udf.loc[user_id,'complaints'])
    udf.to_csv('udf.csv')
    return response

@app.route('/get_main')
def get_main():
    return render_template('main.html')

@app.route('/recommend',methods=['POST'])
def recommend():
    global user_id
    global category
    global sub_category_index
    print()
    x=cat_sub[category]
    x=x[1][sub_category_index]
    x=list(x.split('.'))
    x=x[0]
    # print(x)
    udf=pd.read_csv(x+'/udf.csv',index_col=0)
    pdf=pd.read_csv(x+'/pdf.csv',index_col=0)
    existing_users=list(udf.index)
    # print(udf)
    if user_id in existing_users:
        # print("1")
        products=pdf.index
        u_p=pd.DataFrame(columns=products)
        for x in event_score:
            udf[x]=udf[x].apply(ast.literal_eval)
        for index, row in udf.iterrows():
            new_row={}
            for i in products:
                new_row[i]=0
            # print(new_row)
            for x in event_score:
                sc=event_score[x]
                # df['list_column'].apply(ast.literal_eval)
                # print(type(row[x]))
                # print(x)
                for i in row[x]:
                    # print(i)
                    # break
                    new_row[i]+=sc
            #     break 
            # break
            # print(new_row)
            u_p.loc[u_p.shape[0]] = new_row
            # print(u_p)
            # break
        # print("2")
        u_p.index=udf.index
        u_p=u_p.rename_axis("user_id")
        u_p_t=u_p.T
        u_p_t=u_p_t.rename_axis("prod_id")
        SVD = TruncatedSVD(n_components=10)
        # print(u_p)
        decomposed_matrix = SVD.fit_transform(u_p_t)
        correlation_matrix = np.corrcoef(decomposed_matrix)
        
        # print("hello")
        # user=0
        # print(user_id)
        l=udf.loc[user_id, 'bought']
        # print("3")
        ans=[]
        for x in l:
            y=int(x[4:])-1
            m=list(u_p_t.index[correlation_matrix[y] > 0.80])
        #     print(type(m))
            for z in m:
                ans.append(z)

        def cosine_similarity(u, v):
            dot_product = np.dot(u, v)
            norm_u = np.linalg.norm(u)
            norm_v = np.linalg.norm(v)
            similarity = dot_product / (norm_u * norm_v)
            return similarity
        np_res=np.array(u_p.values)
        num_users = np_res.shape[0]
        
        similarity_matrix_cosine = np.zeros((num_users, num_users))
        # # similarity_matrix_pearson = np.zeros((num_users, num_users))
        # print(type(num_users))
        # print("4")
        for i in range(num_users):
            for j in range(num_users):
                similarity_matrix_cosine[i, j] = cosine_similarity(np_res[i], np_res[j])
        
        indices = list(udf.index)
        user=indices.index(user_id)
        # user=0
        # print("5")
        top_indices = sorted(range(len(similarity_matrix_cosine[user])), key=lambda i: similarity_matrix_cosine[user][i], reverse=True)[:5]
        top_indices.remove(user)
       
        for x in top_indices:
        #     print(x)
           
            m=udf.iloc[x,udf.columns.get_loc('bought')]
            # print("hello")
            for z in m:
                ans.append(z)
        
        ans=list(set(ans))
        # print("hello")
        res=[]
        for i in range(12):
            dummy={}
            dummy['prod_id']=ans[i]
            dummy['name']=pdf.loc[ans[i], 'name']
            dummy['image_link']=pdf.loc[ans[i], 'image_link']
            dummy['price']=int(pdf.loc[ans[i], 'price'])
            res.append(dummy)
        
        # for d in res[0]:
        #     print(type(res[0][d]))
        # def obj_dict(obj):
        #     return obj.__dict__

        # json_string = json.dumps(res)
        # fin = json.dumps(res)
        # print(res)
        return res 
    else: 
        dum=pdf.sort_values(by=['score'], ascending=False)
        dum=dum.head(12)
        res=[]
        for index, row in dum.iterrows():
            dummy={}
            dummy['prod_id']=index
            dummy['name']=row['name']
            dummy['image_link']=row['image_link']
            dummy['price']=int(row['price'])
            res.append(dummy)
        
        # print(res)
        # print(res[0])
        # fin = json.dumps(res)
        return res
    # return render_template('main.html')

@app.route('/update',methods=['POST'])
def update():
    # print("hello")
    # global udf
    # global pdf
    global user_id
    global category
    global sub_category_index
    # print()
    x=cat_sub[category]
    x=x[1][sub_category_index]
    x=list(x.split('.'))
    x=x[0]
    # print(x)
    h=x
    udf=pd.read_csv(x+'/udf.csv',index_col=0)
    pdf=pd.read_csv(x+'/pdf.csv',index_col=0)
    for x in event_score:
            udf[x]=udf[x].apply(ast.literal_eval)
    # udf=pd.read_csv('udf.csv')
    # pdf=pd.read_csv('pdf.csv')
    # if(existing):
    #     global user_id
    # else:
    #     user_id
    l1=request.get_json()
    # print(l1)
    existing_users=list(udf.index)
    # print(udf)
    if user_id not in existing_users:
        udf.loc[user_id]= {'view':[], 'saved_for_later':[], 'added_to_cart':[], 'bought':[], 'like':[]}
    for x in l1:
        y=event_score[x]
        l=udf.loc[user_id,x]
        for z in l1[x]:
            if z not in l:
                udf.loc[user_id,x].append(z)
                pdf.loc[z,'score']+=y
    # event_type=request.form.get('event_type')
    # prod_id=request.form.get('prod_id')
    # if prod_id not in udf.loc[user_id,'event_type']:
    #     udf.loc[user_id,'event_type'].append(prod_id)
    #     pdf.loc[prod_id, 'score']+=event_score[event_type]
    udf.to_csv(h+'/udf.csv')
    pdf.to_csv(h+'/pdf.csv')
    # print("done")
    return "hello"

if __name__ == '__main__':
    app.run(debug=True)

# def analyze_complaint(complaint):
    