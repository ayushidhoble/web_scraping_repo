import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, url_for, redirect
from sqlalchemy import Column, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask import Flask, request
from flask_mail import Mail, Message

# from models import Book

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'trytestapp007@gmail.com'
app.config['MAIL_PASSWORD'] = 'trytestapp@123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
recepients_list = ['ayuxm10@gmail.com']


def send_email(subject, msg_body, recepients_list=recepients_list, sender=app.config['MAIL_USERNAME']):
    msg = Message(subject, sender=sender, recipients=recepients_list)
    msg.body = msg_body
    mail.send(msg)
    return "Sent"


DATABASE_URI = 'postgres+psycopg2://postgres:postgres@localhost:5432/web_scrap'

Base = declarative_base()


class Book(Base):
    __tablename__ = 'job_details'
    job_id = Column(String, primary_key=True)
    source = Column(String)
    title = Column(String)
    job_location = Column(String)
    job_post_date = Column(DateTime)
    company_name = Column(String)
    company_url = Column(String)
    employment_type = Column(String)
    employer_type = Column(String)
    print("********************************************************************************************")

    def __repr__(self):
        return "<Book(job_id='{}', title='{}', job_location='{}', job_post_date={}, company_name='{}', company_url='{}', employment_type='{}', employer_type='{}')>" \
            .format(self.job_id, self.title, self.job_location, self.job_post_date, self.company_name, self.company_url,
                    self.employment_type, self.employer_type)


@app.route('/')
def demo():
    # return render_template("home_try.html")
    # return render_template("try.html")

    return render_template("landing.html")


@app.route('/linkedIn/', methods=['POST', 'GET'])
def linkedin():
    global data
    if request.method == "GET":
        url = "https://www.linkedin.com/jobs/search"

        headers = {'authority': 'in.linkedin.com'}

        print("INSIDE GET", request.args)
        # print("PAGEVALUE", request.args.get("page"))
        page = request.args.get("page", 1)

        print(page)
        page_size = request.args.get("pageSize", 20)
        search_keyword = urllib.parse.quote_plus(request.args.get("search", "Ruby"))
        search_location = urllib.parse.quote_plus(request.args.get("location", "united state"))
        filter_time = request.args.get("date")
        print("FILTER TIME", filter_time)
        if filter_time == "today":
            search_time = "1"
        elif filter_time == "week":
            search_time = urllib.parse.quote_plus("1,2")
        elif filter_time == "month":
            search_time = urllib.parse.quote_plus("1,2,3,4")
        else:
            search_time = ""
        # search_time = urllib.parse.quote_plus(request.args.get("f_TP", ""))
        search_job_type = urllib.parse.quote_plus(request.args.get("jobtype", ""))

        # "trk": "homepage-jobseeker_jobs-search-bar_search-submit"
        param_dict = {"url": url, "search_keyword": search_keyword, "job_location": search_location,
                      "search_time": search_time, "page": page, "trk": "public_jobs_jobs-search-bar_search-submit",
                      "search_job_type": search_job_type, }
        # print(param_dict)

        request_url = """{url}?keywords={search_keyword}&location={job_location}&trk={trk}&f_TP={search_time}&redirect=false&position=1&pageNum={page}&f_JT={search_job_type}""".format(
            **param_dict)
        # print(request_url)
        response = requests.get(request_url, headers=headers).content
        soup = BeautifulSoup(response, "html.parser")
        main_div = soup.find("div", {"class": "results__container results__container--two-pane"})

        single_list = main_div.find_all("li")
        data_list = []

        engine = create_engine(DATABASE_URI)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for job in single_list:
            # companyLogoUrl = i.find("img").src
            # title_url = i.find("a").href
            job_id = str(job.attrs["data-id"])

            # print(job_id)

            single_list_div = job.find("div")

            job_title = single_list_div.find("h3").text
            company_name = single_list_div.find("h4").text
            companyPageUrl = single_list_div.find("h4").text
            try:
                summary = single_list_div.find("p").text
            except Exception as e:
                summary = ''
            job_location = single_list_div.find("span").text

            job_post_date = single_list_div.find("time").text
            employmentType = single_list_div.find("span").text

            data = {'title': job_title, 'companyName': company_name, 'companyPageUrl': companyPageUrl,
                    'jobLocation': {"displayName": job_location},
                    'summary': summary, 'postedDate': job_post_date, 'job_id': job_id, employmentType: 'employmentType'}

            p = Book()

            if job_post_date == "1 day ago":
                current_date = datetime.datetime.now().date()
                yesterday_date = current_date - datetime.timedelta(days=1)
                p.job_post_date = yesterday_date
                print(p.job_post_date)

                print("Insert succesfully")
                p.job_id = data.get("job_id")
                p.source = "LinkedIn"
                p.title = data.get('title')
                p.job_location = data.get('jobLocation').get('displayName')
                p.company_name = data.get('companyName')
                p.company_url = data.get('companyPageUrl')
                p.employment_type = data.get('employmentType')
                p.employer_type = data.get('employerType')
                try:
                    session.add(p)
                    session.commit()
                except (IntegrityError, InvalidRequestError) as e:
                    print("SQLALCHECY EXCEPTION")
                    print(e)
                except Exception as e:
                    print("EXCEPTION")
                    print(e)

                msg_body = "Hello dear sir/ ma'am, " \
                           "This mail is regarding job updates from linkedin . you can check it by using " \
                           "link. Please click here {}  " \
                           " thank you".format(request.base_url)
                print(request.base_url)
                send_email('TEST EMAIL', msg_body)

            else:
                print("nothing match")

            data_list.append(data)

            # print(current_date)

            # if job_post_date == "1 day ago":
            #     found = job_openings.count_documents(data)
            #     if not found:
            #         result = job_openings.insert(data)
            #         print("data of database:", result)

            # print(data)

        ret_dict = {"data_list": data_list, "next_page_count": int(page) + 1, "previous_page_count": int(page) - 1,
                    "search_keyword": search_keyword,
                    "search_location": search_location, "search_time": search_time, "search_job_type": search_job_type}
        print(ret_dict)
        return ret_dict  # return render_template("sample_template.html", data_list=data_list, search_keyword=search_keyword)

    else:
        print("no keyword found")


@app.route('/home/', methods=['POST'])
@app.route('/home/<search>', methods=['GET', 'POST'])
def dice(search=None, job_post_date=None):
    if request.method == "GET":
        url = "https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
        # url = "https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search?location=Maharashtra,%20India&page=1&pageSize=20&facets=employmentType%7CpostedDate%7CworkFromHomeAvailability%7CemployerType%7CeasyApply%7CisRemote&fields=id%7CjobId%7Csummary%7Ctitle%7CpostedDate%7CjobLocation.displayName%7CdetailsPageUrl%7Csalary%7CclientBrandId%7CcompanyPageUrl%7CcompanyLogoUrl%7CpositionId%7CcompanyName%7CemploymentType%7CisHighlighted%7Cscore%7CeasyApply%7CemployerType%7CworkFromHomeAvailability%7CisRemote&culture=en&recommendations=true&interactionId=0&fj=true&includeRemote=true"
        headers = {'authority': 'job-search-api.svc.dhigroupinc.com',
                   'x-api-key': '1YAt0R9wBg4WfsF9VB2778F5CHLAPMVW3WAZcKd8'}

        print("INSIDE GET", request.args)
        print("PAGEVALUE", request.args.get("page"))
        page = request.args.get("page", 1)
        print("...................................................")
        print(page)
        page_size = request.args.get("pageSize", 20)
        search_keyword = request.args.get("search", "Ruby")
        search_location = request.args.get("location", "united state")
        filter_time = request.args.get("date")
        if filter_time == "today":
            search_time = "ONE"
        elif filter_time == "week":
            search_time = urllib.parse.quote_plus("SEVEN")
        else:
            search_time = ""
        # search_time = urllib.parse.quote_plus(request.args.get("f_TP", ""))
        job_type = urllib.parse.quote_plus(request.args.get("jobtype", ""))
        if job_type == "F":
            search_job_type = "FULLTIME"
        elif job_type == "O":
            search_job_type = "THIRD_PARTY"
        elif job_type == "C":
            search_job_type = "CONTRACTS"
        elif job_type == "P":
            search_job_type = "PARTTIME"
        else:
            search_job_type = ""
        param_dict = {"url": url, "search_keyword": search_keyword, "job_location": search_location,
                      "search_time": search_time, "page": page, "page_size": page_size,
                      "search_job_type": search_job_type}
        # & countryCode2 = US
        request_url = """{url}?q={search_keyword}&filters.employmentType={search_job_type}&filters.postedDate={search_time}&location={job_location}&radius=30&radiusUnit=mi&page={page}&pageSize={page_size}&facets=employmentType%7CpostedDate%7CworkFromHomeAvailability%7CemployerType%7CeasyApply&fields=id%7CjobId%7Csummary%7Ctitle%7CpostedDate%7CjobLocation.displayName%7CdetailsPageUrl%7Csalary%7CclientBrandId%7CcompanyPageUrl%7CcompanyLogoUrl%7CpositionId%7CcompanyName%7CemploymentType%7CisHighlighted%7Cscore%7CeasyApply%7CemployerType%7CworkFromHomeAvailability&culture=en&recommendations=true&interactionId=0&fj=true""".format(
            **param_dict)
        print(request_url)
        response = requests.get(request_url, headers=headers)
        data_list = response.json().get("data", [])

        engine = create_engine(DATABASE_URI)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for job_dict in data_list:
            p = Book()
            p.job_post_date = job_dict.get('postedDate')
            current_date = datetime.datetime.now().date()
            yesterday_date = current_date - datetime.timedelta(days=1)
            # print(yesterday_date)
            # print(p.job_post_date)

            if p.job_post_date == yesterday_date:
                p.job_id = job_dict.get("jobId")
                p.source = "Dice"
                p.title = job_dict.get("title")
                p.job_location = job_dict.get('jobLocation').get('displayName')
                p.company_name = job_dict.get('companyName')
                p.company_url = job_dict.get('companyPageUrl')
                p.employment_type = job_dict.get('employmentType')
                p.employer_type = job_dict.get('employerType')
                try:
                    session.add(p)
                    print("Insert succesfully")
                    session.commit()
                except (IntegrityError, InvalidRequestError) as e:
                    print("SQLALCHECY EXCEPTION")
                    print(e)
                except Exception as e:
                    print("EXCEPTION")
                    print(e)
                msg_body = "Hello dear sir/ ma'am, " \
                           "This mail is regarding job updates from  Dice. you can check it by using " \
                           "link. Please click here {}  " \
                           " thank you".format(request.base_url)
                print(request.base_url)
                send_email('TEST EMAIL', msg_body)

            else:
                print("not insert")

        ret_dict = {"data_list": data_list, "next_page_count": int(page) + 1, "previous_page_count": int(page) - 1,
                    "search_keyword": search_keyword,
                    "search_location": search_location, "search_time": search_time, "search_job_type": search_job_type}
        return ret_dict
    else:
        print(request.form)
        search_keyword = request.form.get("search")
        if search_keyword:
            print(url_for('home'))
            return redirect(url_for('home') + search_keyword)
        else:
            return "SEARCH KEWORD NOT FOUND"


@app.route('/common/', methods=['GET'])
def common():
    print(request.args)
    select_source = request.args.get("source")
    print(select_source)
    if select_source == "linkedin":
        print("INSIDE LINKEDIN")
        data = linkedin()
        data["selected_source"] = "linkedin"
        print(data.keys())
    else:
        print(select_source)
        print("INSIDE DICE")
        data = dice()
        data["selected_source"] = "dice"
        print(data.keys())
    return render_template("demo.html", **data)


if __name__ == "__main__":
    app.run(debug=True)
