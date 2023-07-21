from datetime import datetime
import openai
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import argparse
import logging



def clean_up_web_text(text):
    # Remove new lines
    text = text.replace('\n', ' ')
    # Replace multiple spaces with a single space
    text = re.sub(' +', ' ', text)
    # Replace consecutive line breaks with a single space
    text = re.sub('\n+', ' ', text)
    # Strip leading and trailing spaces
    text = text.strip()
    return text


def fetch_website_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract the text of the webpage
    text = soup.get_text()
    # Clean up the text
    text = clean_up_web_text(text)
    return text


def get_company_name(web_text):
    print("Getting basic information...")
    res = openai.ChatCompletion.create(
        model=fast_model,
        messages=[
            {"role": "system", "content": "You are helpful AI who specializes in finding the names of companies"},
            {"role": "user", "content": example_company_description},
            {"role": "assistant", "content": "CogniWave Consulting"},
            {"role": "user", "content": web_text}
        ]
    )
    return res['choices'][0]['message']['content']


def get_company_description(web_text):
    print("Understanding what your company does...")
    # Get the 5 most relevant pages before building this
    # TODO change this to "Elevator Pitch"
    res = openai.ChatCompletion.create(
        # Using the smart model here because if this is wrong for any reason I think people will throw out the report
        model=fast_model if test_mode else smart_model,
        messages=[
            {"role": "assistant", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": "Descibe what this company does: " + web_text},
        ]
    )
    return res['choices'][0]['message']['content']


def describe_user_problem(user_input):
    print("Understanding the problem...")
    res = openai.ChatCompletion.create(
        # Using the smart model here because this is what's going to hook people into reading the report
        model=fast_model if test_mode else smart_model,
        messages=[
            {"role": "system", "content": "You are an experienced marketer who specializes in describing the problems that users have in easy-to-understand language, as if you were describing them to a fellow team member with just one year of experience"},
            {"role": "user", "content": example_problem_statement},
            {"role": "assistant", "content": example_problem_response},
            {"role": "user", "content": user_input}
        ]
    )
    return res['choices'][0]['message']['content']


def generate_kpi():
    if report_data[explain_problem_key]:
        print("Generating KPI...")
        kpi_list = openai.ChatCompletion.create(
            # Using the smart model here because this is what's going to hook people into reading the report
            model=fast_model,
            messages=[
                {"role": "system", "content": "You are an expert business analyst who specializes in generating KPIs for businesses"},
                {"role": "user", "content": "What are 10 KPIs that I could use to measure this problem?\n\n" + \
                    example_problem_statement + "\nHere's a bit about my business:\n" + example_company_description},
                {"role": "assistant",
                 "content": example_kpi_list},
                {"role": "user", "content": "What are 10 KPIs that I could use to measure this problem?\n\n" + \
                    user_prompt + "\nHere's a bit about my business:\n" + report_data[company_description_key]},
            ]
        )
        kpi_list = kpi_list['choices'][0]['message']['content']
        print("Validating KPI...")
        res = openai.ChatCompletion.create(
            # Using the smart model here because this is what's going to hook people into reading the report
            model=fast_model if test_mode else smart_model,

            messages=[
                {"role": "system", "content": "You are an expert business analyst from YCombinator who specializes in selecting the right KPIs for businesses"},
                {"role": "user", "content": "Select the KPI that makes the most sense to measure our problem with: " + example_kpi_list + \
                    "\n Our problem: " + example_problem_statement + "\nHere's a bit about my business:\n" + example_company_description},
                {"role": "assistant",
                 "content": example_kpi_selection_response},
                {"role": "user", "content": "Select the KPI that makes the most sense to measure our problem with: " + kpi_list + \
                    "\n Our problem: " + report_data[explain_problem_key] + "\nMore about our company: " + report_data[company_description_key]},
            ]
        )
        return res['choices'][0]['message']['content']
    else:
        print(
            "Unable to generate KPI, report_data[explain_problem_key] is null. Closing the program")
        exit()


def generate_hypothesis(web_copy):
    print("Thinking up a hypothesis...")
    hypothesis_list = openai.ChatCompletion.create(
        # Using the smart model here because this is what's going to hook people into reading the report
        model=fast_model if test_mode else smart_model,

        messages=[
            {"role": "system", "content": "You are a data-driven marketer who specializes in generating hypotheses for businesses"},
            # {"role": "user", "content": "What are 10 KPIs that I could use to measure this problem?\n\n"+ example_problem_statement +"\nHere's a bit about my business:\nCogniWave Consulting is a company that provides custom artificial intelligence (AI) solutions specifically designed for marketers. Through a blend of expertise in marketing and AI technology, they create content aimed at high conversion rates. \n\nTheir offerings include:\n\n1. AI Content Creation - They create an AI powered by the client's specific customer data which generates content at a standard expected by the client, converting marketers' roles from content generators to content reviewers.\n\n2. Interactive Customer Analytics - They construct hyper-realistic simulations of clients' users, allowing them to test data-based hypotheses in various scenarios.\n\n3. AI-Infused CRM - Through AI integration, clients can engage in conversation with all leads and customers in their CRM concurrently, personalizing messages at appropriate times.\n\n4. ChatGPT Training and Support – They offer support and training on a tool called ChatGPT focusing on 'prompt engineering competency', which they believe is a crucial skill in the modern world. \n\nIn addition to these services, CogniWave Consulting also hosts a blog where they discuss topics related to AI technology and marketing."},
            # {"role": "assistant",
            #  "content": "1/ Conversion Rate: The percentage of visitors who contact you after visiting your landing page.\n2/Bounce Rate: The percentage of visitors who leave your website after viewing only one page.\n3/Time on Page: The average amount of time visitors spend on your landing page.\n4/Page Views per Visit: The average number of pages a visitor views during a single visit.\n5/Click-Through Rate (CTR): The percentage of visitors who click on a specific link on your landing page.\n6/Return Visitor Rate: The percentage of visitors who return to your website after their initial visit.\n7/Cost per Acquisition (CPA): The average cost to acquire a customer who contacts you.\n8/Engagement Rate: The percentage of visitors who interact with your site in some way, such as clicking on a link or filling out a form.\n9/Lead-to-Customer Rate: The percentage of leads (people who contacted you) who become customers.\n10/Blog Post Engagement: The number of views, shares, comments, and likes on your blog posts."},
            {"role": "user", "content":
                "What are 5 ways that we might be able to improve our " + report_data[kpi_used_to_measure_problem_key] + "?\n\nOur business: " + report_data[company_description_key] + "\nOur problem " + report_data[explain_problem_key] + "\nour website copy: " + web_copy}
        ]
    )
    hypothesis_list = hypothesis_list['choices'][0]['message']['content']
    print("Refining my theories...")
    res = openai.ChatCompletion.create(
        model=fast_model if test_mode else smart_model,

        messages=[
            {"role": "system", "content": "You are an experienced data-driven marketer"},
            {"role": "user",
                "content": "Given the business we are in, the problem that we are facing, and the KPI that we want to use to measure whether or not we're solving our problem, which hypothesis do you think is most accurate? Explain your reasoning (see below)" + "\nHypothesis list: " + example_hypothesis_list + "\n\n" + example_company_description + "\n\n" + example_problem_response + "\n\n" + example_kpi_selection_response},
            {"role": "assistant",
             "content": example_hypothesis_response},
            {"role": "user", "content": "Given the business we are in, the problem that we are facing, and the KPI that we want to use to measure whether or not we're solving our problem, which hypothesis do you think is most accurate? Explain your reasoning (see below)" + "\nHypothesis list: " + hypothesis_list + "\n\n" + report_data[
                company_description_key] + "\n\n" + report_data[explain_problem_key] + "\n\n" + report_data[kpi_used_to_measure_problem_key]}
        ]
    )
    return res['choices'][0]['message']['content']


def generate_test():
    print("Generating ideas to test the hypothesis...")
    test_list = openai.ChatCompletion.create(
        model=fast_model if test_mode else smart_model,

        messages=[
            {"role": "system", "content": "You are a data-driven marketer who specializes in building tests to validate hypotheses"},
            {"role": "user", "content": "What are 10 tests that could work for testing my hypothesis? " + example_report_1},
            {"role": "assistant", "content": example_test_10_response},
            {"role": "user", "content": "What are 10 tests that could work for testing my hypothesis? " +
                str(report_data)}
        ]
    )
    test_list = test_list['choices'][0]['message']['content']

    res = openai.ChatCompletion.create(
        model=fast_model if test_mode else smart_model,

        messages=[
            {"role": "system", "content": "You are a data-driven marketer who specializes in building tests to validate hypotheses"},
            {"role": "user", "content": "Pick a test that you recommend, and write a 1-paragraph explanation as to how you think it will help to validate/invalidate the hypothesis. I'll include your test in the report below: " +
                example_test_10_response + "\n\n" + example_report_1},
            {"role": "assistant", "content": example_test_selection_response},
            {"role": "user", "content": "Pick a test that you recommend, and write a 1-paragraph explanation as to how you think it will help to validate/invalidate the hypothesis " +
                test_list+"\n\n" + str(report_data)}
        ]
    )
    return res['choices'][0]['message']['content']


def figure_out_what_we_can_expect_to_learn():
    print("Making sure the test fits with what we want to learn...")
    res = openai.ChatCompletion.create(
        model=fast_model if test_mode else smart_model,

        messages=[
            {"role": "system", "content": "You are a data-driven marketer who specializes in building tests to validate hypotheses"},
            # {"role": "user", "content": "Pick a test that you recommend, and write a 1-paragraph explanation as to how you think it will help to validate/invalidate the hypothesis. I'll include your test in the report below: " + example_test_10_response + "\n\n" + example_report_1},
            # {"role": "assistant", "content": example_test_selection_response},
            {"role": "user",
                "content": "Based on my report (linked below), what can I expect to learn from the test that I've outlined? Explain how it will validate or invalidate my hypothesis \n\n" + str(report_data)}
        ]
    )
    return res['choices'][0]['message']['content']


def how_to_perform_test():
    print("Writing a guide for performing this test...")

    res = openai.ChatCompletion.create(
        model=fast_model if test_mode else smart_model,

        messages=[
            {"role": "system", "content": "You are a data-driven marketer who specializes in building tests to validate hypotheses"},
            {"role": "user",
                "content": "How can I perform the test (in a tool agnostic way) detailed in my report? How can I ensure that my data is clean? \n\n " + example_report_2},
            {"role": "assistant", "content": example_test_steps},
            {"role": "user",
                "content": "How can I perform the test (in a tool agnostic way) detailed in my report? How can I ensure that my data is clean? \n\n" + str(report_data)}
        ]
    )
    return res['choices'][0]['message']['content']


def generate_title():
    print("Prepping the report...")
    res = openai.ChatCompletion.create(
        model=fast_model,
        messages=[
            {"role": "system", "content": "You are a senior business analyst who specializes in creating accurate titles"},
            {"role": "user", "content": "What should I title this report?\n\n " + example_report_2},
            {"role": "assistant", "content": example_title},
            {"role": "user",
                "content": "What should I title this report?\n\n " + str(report_data)}
        ]
    )
    return res['choices'][0]['message']['content']

def get_relevant_tech_stack():
    # tell the user which parts of their tech stack we need to see
    # have the user give us the tech stack
    # figure out if the user gave us all the software required. If not, tell them which software they need and pick it for them
    # give them a step by step guide for setting it up
    return None

def main(url, user_prompt, test_mode):
    if test_mode == True:
        print("Test mode enabled. Only using " + fast_model)
        test_mode = True
    else:
        print("Prod mode enabled. Using " + smart_model + " and " + fast_model)
        test_mode = False
    
    report_data[company_name_key] = get_company_name(fetch_website_text(url))
    report_data[company_description_key] = get_company_description(
        fetch_website_text(url))
    # in the company description, replace new lines with spaces
    report_data[company_description_key] = report_data[company_description_key].replace(
        '\n', ' ')
    report_data[explain_problem_key] = describe_user_problem(
        user_prompt).replace('\n', ' ')
    report_data[kpi_used_to_measure_problem_key] = generate_kpi().replace(
        '\n', ' ')
    report_data[hypothesis_key] = generate_hypothesis(
        web_copy=fetch_website_text(url)).replace('\n', ' ')
    report_data[recommended_test_key] = generate_test().replace('\n', ' ')
    report_data[what_we_can_expect_to_learn_key] = figure_out_what_we_can_expect_to_learn(
    ).replace('\n', ' ')
    report_data[how_to_perform_test_key] = how_to_perform_test()
    report_data[report_title_key] = generate_title()
    # report_data[tech_stack_key] = get_relevant_tech_stack()
    return None


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
smart_model = "gpt-4"
fast_model = "gpt-3.5-turbo"
company_name_key = "Company Name"
report_date_key = "Report Date"
algorithm_version_key = "Algorithm Version"
report_title_key = "Report Title"
company_description_key = "Company Description"
explain_problem_key = "Explanation of Problem"
kpi_used_to_measure_problem_key = "KPI Used To Measure Problem"
hypothesis_key = "Hypothesis"
recommended_test_key = "Recommended Test"
what_we_can_expect_to_learn_key = "What We Can Expect To Learn"
how_to_perform_test_key = "How To Perform Test"
# tech_stack_key = []

example_problem_statement = "I run CogniWave Consulting. Right now, of the 133 people that have come to my landing page this week, 0 have contacted me"
example_kpi_selection_response = "Bounce Rate: The percentage of visitors who leave your website after viewing only one page."
example_kpi_list = "1/ Conversion Rate: The percentage of visitors who contact you after visiting your landing page.\n2/Bounce Rate: The percentage of visitors who leave your website after viewing only one page.\n3/Time on Page: The average amount of time visitors spend on your landing page.\n4/Page Views per Visit: The average number of pages a visitor views during a single visit.\n5/Click-Through Rate (CTR): The percentage of visitors who click on a specific link on your landing page.\n6/Return Visitor Rate: The percentage of visitors who return to your website after their initial visit.\n7/Cost per Acquisition (CPA): The average cost to acquire a customer who contacts you.\n8/Engagement Rate: The percentage of visitors who interact with your site in some way, such as clicking on a link or filling out a form.\n9/Lead-to-Customer Rate: The percentage of leads (people who contacted you) who become customers.\n10/Blog Post Engagement: The number of views, shares, comments, and likes on your blog posts."
example_company_description = "CogniWave Consulting is a B2B software consulting company that provides custom artificial intelligence (AI) solutions specifically designed for marketers. Their target market likely includes low-tech businesses doing $10M-$50M in annual revenue who have no programmers on staff but want to implement AI. They solve their customers' problems through a blend of expertise in marketing and AI technology. \n\nTheir offerings include:\n\n1. AI Content Creation - They create an AI powered by the client's specific customer data which generates content at a standard expected by the client, converting marketers' roles from content generators to content reviewers.\n\n2. Interactive Customer Analytics - They construct hyper-realistic simulations of clients' users, allowing them to test data-based hypotheses in various scenarios.\n\n3. AI-Infused CRM - Through AI integration, clients can engage in conversation with all leads and customers in their CRM concurrently, personalizing messages at appropriate times.\n\n4. ChatGPT Training and Support – They offer support and training on a tool called ChatGPT focusing on 'prompt engineering competency', which they believe is a crucial skill in the modern world. \n\nIn addition to these services, CogniWave Consulting also hosts a blog where they discuss topics related to AI technology and marketing."
example_problem_response = "Your problem is essentially one of conversion rate optimization (CRO). In digital marketing terms, the conversion rate is the percentage of users who take a desired action on a website. In your case, the desired action is contacting you after visiting your landing page. Currently, your conversion rate is zero, as none of the 133 visitors to your landing page have reached out to you. This suggests that while your website is attracting traffic, it's not compelling visitors to engage further with your business."
example_hypothesis_response = "Given the problem at hand and your KPI, I would posit that personalizing the sales process by introducing regular follow-ups post meeting could be the most accurate. Here's the reasons for this: 1. Since the problem you face is within client conversion and not visitor conversion, tailoring your approach by analysing the specific needs of the leads might be beneficial. The utilization of AI-driven analytics to identify their needs and showcase solutions specific to them during meetings could help your prospects to see you not just as a service provider but as a problem solver. This can help build trust and effectiveness in your sales proposal, eventually leading to better conversion rates. Additionally, decisions are not made immediately after a sales meeting, especially for complex AI-oriented solutions like yours. There are generally numerous stakeholders on their end who might need to weigh in or approve the decision. An effective personalized follow-up system keeps your value proposition top of mind for your potential clients, and continually reinforces the benefits of your solution, bolstering the chance for conversion. It is also recommended that post-meeting, you solicit feedback from potential clients who chose not to move forward. Understanding their concerns will provide you with insights that may help refine your sales approach and improve your lead conversion rate."
example_test_10_response = "Simplicity Test: Simplify the language used in your service descriptions and measure if this leads to an increase in conversion rates. Educational Content Test: Develop and distribute educational content that explains your services in non-technical terms. Monitor if this leads to higher engagement and conversion rates. A/B Testing on Service Explanation: Perform A/B tests with different versions of service explanations (one technical, one simple) and see which one yields a better conversion rate. Sales Script Test: Have your sales team use a simplified script when explaining your services to prospective clients. Compare the conversion rates with the previous script. Customer Feedback: Ask for feedback from potential clients who did not convert. Try to understand if the complexity of your service explanation was a factor in their decision. Lead Quality Analysis: Analyze the quality of your leads before and after implementing a more straightforward service explanation. Check if the change attracts better-suited leads for your services. Web Analytics: Monitor your website analytics before and after making changes to your service explanations. Check for increases in time spent on your website, pages per visit, and other engagement metrics. Client Onboarding Test: Compare the onboarding process of clients who were given the simplified service explanation versus those who were not. Measure differences in time to onboard and initial satisfaction rates. Competitor Analysis: Compare your service explanations and conversion rates to those of your competitors who use simpler language. Note any correlation between simplicity and conversion rates. Survey Test: Conduct surveys with potential clients who didn't convert, asking them to rate their understanding of your services. Use this feedback to identify where you can improve your explanations."
example_report_1 = "Report Data: ------------------ Company Name: CogniWave Consulting Report Date: July 21, 2023 Algorithm Version: 0.0.1 Report Title: Company Description: CogniWave Consulting is an Artificial Intelligence (AI) based company that offers custom AI solutions primarily for marketers. These AI solutions are designed by experienced product marketers to deliver high-converting content. They offer AI-generated content, which is created by training an AI on a client's specific customer data. This results in content that matches the caliber the client's team is used to, transforming marketers from content creators to reviewers.   In addition, the company provides Interactive Customer Analytics, which allow clients to test data-based hypotheses in numerous scenarios via hyper-realistic simulations of their users. They also offer AI-infused Customer Relationship Management (CRM) services, enabling engaging conversations with every lead and customer.   CogniWave Consulting further provides ChatGPT Training and Support, emphasizing the importance of prompt engineering competency in navigating the ever-evolving tech infrastructure. They discuss AI technology and marketing strategies on their blog and offer a newsletter for updates. Explanation of Problem: Your problem here seems to be on two front. First, it's about effective lead conversion - in other words, promising prospective clients aren't turning into paying customers after initial meetings. This could be due to a variety of factors - maybe you're not meeting their needs or expectations fully, or perhaps there's a mismatch between what your service offers and what the clients are looking for.   Secondly, this situation could also reveal issues with the qualification of your leads. This means that the clients reaching out via your website may not be the right fit for your consulting services. They might not fully understand what you offer, or they are not the decision-makers within their own company, hence, unable to commit to your services even if they wanted to. Both of these problems require different strategies to be addressed effectively. KPI Used To Measure Problem: Conversion Rate: The percentage of potential clients who sign with you out of the total meetings held and Close Rate: The percentage of potential clients who sign with you out of the total number of potential clients generated. These KPIs seem the most relevant given your problem with ineffective lead conversion. Understanding these metrics could help you pinpoint and address issues within your sales process or communication strategy. Hypothesis: Considering the nature of your business and the current problems you are facing, I would say that the hypothesis Improve Service Explanation could be the most accurate one to address while looking at your specific KPIs. Here's my rationale: 1. B2B AI Solutions: Since your primary market is low-tech businesses wanting to transition into using AI, this indicates that the customers might not be overly familiar with AI concepts. While your services are complex and detailed, your service explanation needs to be tailored to this audience. It's likely that the technical language used to describe your services might be too complex for your prospective clients, causing them to not fully grasp the benefits of your product. 2. Conversion and Close Rates: Since the problem indicated is low conversions after meetings, a more straightforward explanation of your services could assist your sales team in explaining the value proposition to potential customers. If leads better understand the services offered, they are more likely to convert. Additionally, simpler service explanations might attract more quality leads that better fit your ICP. This could inherently increase the close rate by way of attracting leads that are better suited for your services. 3. Visitor to Customer Journey: A clear service explanation could also help visitors self-identify if they are a good fit for your services and could benefit from it. This can filter out irrelevant leads upfront, saving your sales team's time and make the journey from a visitor to a customer more straightforward for high-quality leads. However, it's important to note that while I think this hypothesis is likely to have the most impact, it doesn't necessarily mean the others won't be beneficial. These points could be viewed as pieces of a larger puzzle, and a holistic approach where each aspect is improved upon might yield the best result. In order to validate this or any hypothesis, consider running A/B tests or small experiments to determine which changes have a significant impact on your KPIs."
example_test_selection_response = "I recommend conducting the A/B Testing on Service Explanation. In this test, you create two versions of your service explanations: one that is technical (the current version) and another one that is simplified and more accessible for your target audience. The aim is to compare the conversion rates of potential clients who are exposed to these two different versions. If the simplified version yields a significantly higher conversion rate, it can validate the hypothesis that a more straightforward explanation of your services can increase conversions. On the other hand, if there is no significant difference in conversion rates or if the technical version performs better, it would invalidate the hypothesis. A/B testing is a scientifically rigorous method for testing hypotheses because it directly compares the outcomes of two different approaches, controlling for other variables that could influence the result. Therefore, it would provide solid evidence for whether improving service explanation could solve your conversion issue."
example_hypothesis_list = "1. Highlighting Value of Your Services: Currently, it's explicit how your services work mechanically, but the tangible value these bring to a business in the real world can be made more prominent. This includes the measurable increases in efficiency, revenue, or lower costs from your AI content solutions and customer analytics. 2. More Compelling Call-to-Actions: The current 'Get Started' CTA could be more compelling. The language should more directly emphasize the benefits of starting with your services. For example, 'Boost your marketing efficiency now!' 3. Utilize Social Proof: Integrating customer testimonials or case studies into your website can significantly enhance your potential clients' trust in your services. Such testimonials can illustrate the real-world impacts of your solutions. 4. Improve the User Navigation Experience: Make your website's user journey clearer. Precise and intuitive navigation can lead potential customers effortlessly through the copy, building their understanding and excitement about your offerings seamlessly. 5. More Targeted Messaging: Adjust the website copy to cater directly to the businesses you're targeting. Being explicit about specific industries you've had success in or highlighting particular challenges that your AI solutions can tackle, can make your services more attractive to the particular sectors you are targeting."
example_test_steps = "To perform this test, follow these steps: 1. **Define your variable groups:** The variable you are testing here is the sales approach, which is either personalized or generic. Therefore, your two groups are 'personalized engagement' and 'generic engagement'. 2. **Randomly assign clients to each group:** You want to ensure that the clients in each group are equivalent except for the variable you're testing to avoid bias. The likelihood of a potential client signing up should be independent of their group assignment. An automated process for group assignment can be helpful in ensuring randomness. 3. **Apply the different sales approaches:** For the 'personalized engagement' group, you'll want to heavily leverage your AI solutions to tailor your sales pitches and interactions to each individual client. Conversely, for the 'generic engagement' group, keep the pitch standardized across all clients. 4. **Measure the outcomes:** Track the win rate from each group of clients. The win rate is calculated by dividing the number of potential clients who sign with you by the total number of potential clients engaged. 5. **Analyze the data:** Determine whether there's a statistically significant difference between the win rates of the two groups. Generally, if the p-value associated with the difference is less than 0.05, it's considered significant. To ensure that your data is clean: 1. **Remove duplicates:** Duplicate data can skew your results. 2. **Deal with missing data:** If relevant data is not captured at some point during the testing process, options include imputing it with a median or mean value, or excluding those instances from analysis. 3. **Check for outliers:** Outliers greatly influence the mean and standard deviation of your data, distorting the actual picture. 4. **Verify data entry:** Typos or data entry errors can dramatically impact your results."
example_report_2 = '''{'Company Name': 'CogniWave Consulting', 'Report Date': 'July 21, 2023', 'Algorithm Version': '0.0.1', 'Report Title': '', 'Company Description': 'CogniWave Consulting specializes in creating custom AI solutions for marketers. They craft AI tools guided by experienced product marketers for optimal content creation that is designed to be highly-converting. They provide automated content generation, leveraging AI to create high-quality content based on specific customer data and ultimately shift the role of marketers to content reviewers rather than content generators.   CogniWave Consulting also offers interactive customer analytics by creating hyper-realistic simulations of your users, allowing easy testing of data-based theories in multiple scenarios. Additionally, they integrate AI into CRM systems to facilitate engaging, personalized and timely conversations with every customer and lead.   Furthermore, they provide training and support on ChatGPT and prompt engineering competency to ensure marketers can excel in a future built on the next generation of infrastructure. They also run a blog where they share insights and knowledge on topics such as AI and marketing strategies.', 'Explanation of Problem': "Alright, so your issue is focused on client conversion after initial meetings. Quite simply, you are setting up meetings with potential clients who find you through your website, but you're not able to convert them into signed clients. This could indicate a gap in the way you're presenting your business, offerings, or value proposition during these meetings. A major part of dealing with this could be about refining your communication and sales pitch or maybe tailoring your services better according to the needs and pain points of these potential clients. It's about turning these prospects into clients who believe you can resolve their issues or help them achieve their goals.", 'KPI Used To Measure Problem': 'The most relevant KPI to measure your problem would be "Lead-to-Customer Conversion Rate: The percentage of leads that convert into paying customers." This KPI directly addresses your issue of converting potential clients from meetings into signed clients. It will help gauge how successful you are in convincing your leads to become customers after having initiated contact through a meeting. Tracking and improving this metric can lead to more signed clients, improving your business\'s profitability.', 'Hypothesis': 'Based on your business, the problem you\'re facing, and the KPI to measure the problem, I would suggest that hypothesis number 2: "Optimize Meeting Presentation and Sales Pitch" is the best to focus on.  Here is my reasoning:  Given the nature of your business, you are providing highly technical B2B solutions, namely, AI solutions for marketers. Your target clientele have revenue between $10M-$50M and lack programming staff, indicating they may not have a sophisticated understanding of AI solutions. Therefore, they would require a clear and detailed explanation to understand how your services can add value.  The problem you are experiencing is that while you are attracting potential clients and having meetings with them, you are not able to convert them into paying customers. This indicates that while clients are initially attracted to your services, they do not see enough value or fully understand it after attending these meetings.  Your KPI is a reflection of this - the Lead-to-Customer Conversion rate. Optimizing your meeting presentation may lead to a higher conversion rate by ensuring the value proposition and application of your services are clearly communicated. Moreover, if your sales pitch and meeting presentations are personalized to address each potential client\'s pain points, it could further improve your conversion rate.  Therefore, focusing on optimizing the meeting strategy might yield a more significant impact in solving the current problem. By enhancing your sales pitch and ensuring that your benefits are clearly communicated, you are more likely to succeed in converting leads into customers. Other hypotheses are also valid and could contribute to improving the situation, but given your specifics, optimizing meeting presentation seems most directly related to the issue at hand.', 'Recommended Test': 'I recommend conducting the Segmentation Test. By grouping your potential customers based on their understanding and needs related to your solutions, you can create tailored presentations and sales pitches. This personalized approach allows you to focus on what is important to each customer segment and speak their language. For example, you might explain your product differently to a CEO than to a technical director. By tracking and comparing the conversion rates of each segment before and after the implementation of the test, you can validate or invalidate the hypothesis that customized communication improves conversion rates. If the conversion rate improves significantly within the segments after implementing personalized presentations and sales pitches, the hypothesis can be validated. On the other hand, if there is no significant improvement or if it deteriorates, the hypothesis would be invalidated. Implementing this test will not only help in validating the hypothesis but can also provide insights into the specific needs and preferences of different customer groups, hence improving customer relationship management.', 'What We Can Expect To Learn': 'The test outlined in your report is the Segmentation Test, and it is expected to validate or invalidate your hypothesis - "Optimize Meeting Presentation and Sales Pitch". This hypothesis suggests that optimizing your meeting strategy can lead to a higher lead-to-customer conversion rate. When you improve your sales pitch to effectively communicate the benefits of your solutions and when you make sure that your presentations are customized to address specific pain points of each client segment, you potentially increase the chances of converting leads into clients.  By conducting the Segmentation Test, you plan to customize the sales pitches and presentations based on the understanding and needs related to your solutions for each customer segment. This test will help validate the hypothesis by evaluating whether this personalized approach improves conversion rates.  By comparing conversion rates of each segment before and after the implementation of personalized pitches and presentations, you will be able to learn whether the customization in communication leads to an improvement in conversion rates, hence validating the hypothesis, or not.  Moreover, performing this test will also provide valuable insights into the specific needs and preferences of different customer groups, which will be beneficial not only for the validation of the current hypothesis but also for the future improvement of the customer relationship management practices.   If the customer conversion rates improve significantly when presentations and sales pitches are tailored, this will validate the hypothesis. However, if there is no significant improvement observed, or worse, if the conversion rates deteriorate, the hypothesis would be considered falsified or refuted.', 'How To Perform Test': ''}'''
example_title = "Improving Client Conversion at CogniWave Consulting"

report_data = {
    company_name_key: "",
    report_date_key: datetime.now().strftime("%B %d, %Y"),
    algorithm_version_key: "0.0.1",
    report_title_key: "",
    company_description_key: "",
    explain_problem_key: "",
    kpi_used_to_measure_problem_key: "",
    hypothesis_key: "",
    recommended_test_key: "",
    what_we_can_expect_to_learn_key: "",
    how_to_perform_test_key: "",
    # tech_stack_key: [],
}

parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Process some inputs.')
parser.add_argument('--url', type=str, help='URL for the company')
parser.add_argument('--user_prompt', type=str, help='User prompt')
parser.add_argument('--test_mode', type=bool, default=False, help='Enable or disable test mode')

args = parser.parse_args()
test_mode = args.test_mode
url = args.url
user_prompt = args.user_prompt
logging.basicConfig(filename='logfile.log', level=logging.INFO, format='%(asctime)s %(message)s')
main(args.url, args.user_prompt, args.test_mode)

print("\n\nReport Data:\n------------------\n")
for key in report_data:
    print(key + ": " + report_data[key] + "\n")
print("Would you like me to execute this plan autonomously? (y/n)")
