from django.db import connections
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from dashboard.models import Course
from dashboard.utils import weekbegend
from olap.models import SummaryCourseVisitsByDayInWeek


class CourseDashboardView(TemplateView):
    template_name = 'dashboard/course_dashboard.html'

    def get(self, request, *args, **kwargs):
        course_id = kwargs.get('course_id')
        self.course = Course.objects.get(pk=course_id)

        self.week_id = int(self.request.GET.get('week_filter', 0))

        if self.week_id == -1:
            return redirect('/overallcoursedashboard?course_id=' + str(self.course.id))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course_weeks = self.course.get_weeks()

        if self.week_id == 0:
            self.week_id = course_weeks[0]

        week_no = course_weeks.index(self.week_id) + 1

        cursor = connections['default'].cursor()

        weekbeg, weekend, begweek_unix, endweek_unix = weekbegend(2015, self.week_id)

        # Pageview Graph - Content
        daytotal = [0, 0, 0, 0, 0, 0, 0]
        summary_course_visits = SummaryCourseVisitsByDayInWeek.objects.filter(date_week=course_weeks[week_no-1], course=self.course).order_by('date_dayinweek')
        for visit in summary_course_visits:
            daytotal[visit.date_dayinweek] = visit.pageviews

        PageViewGraphContentList = ','.join(map(str, daytotal))

        # # Pageview Graph - Communication
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, Pageviews FROM Summary_CourseCommunicationVisitsByDayInWeek WHERE DATE_WEEK = %d  AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # PageViewGraphCommunicationList = ','.join(map(str, daytotal))
        #
        # # Pageview Graph - Assessment
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, Pageviews FROM Summary_CourseAssessmentVisitsByDayInWeek WHERE DATE_WEEK = %d  AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # PageViewGraphAssessmentList = ','.join(map(str, daytotal))
        #
        # # Pageview Graph - Unique Views
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, Pageviews FROM Summary_UniquePageViewsByDayInWeek WHERE DATE_WEEK = %d  AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # PageViewGraphUniqueViewsList = ','.join(map(str, daytotal))
        #
        # # Sparkline - Unique Pageviews
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, Pageviews FROM Summary_UniquePageViewsByDayInWeek WHERE DATE_WEEK = %d  AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # uniquepageviewsbydayinweek = ','.join(map(str, daytotal))
        #
        # # Sparkline - Participating Users
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, Pageviews FROM Summary_ParticipatingUsersByDayInWeek WHERE DATE_WEEK = %d  AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # participantsbydayinweek = ','.join(map(str, daytotal))
        #
        # # Sparkline - Sessions by Day in Week
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, sessions FROM Summary_SessionsByDayInWeek WHERE DATE_WEEK = %d AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # sessionsbydayinweek = ','.join(map(str, daytotal))
        #
        # # Sparkline - Average Session Length by Day in Week
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, session_average_in_minutes FROM Summary_SessionAverageLengthByDayInWeek WHERE DATE_WEEK = %d  AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # averagesessionlengthbydayinweek = ','.join(map(str, daytotal))
        #
        # # Sparkline - Average Pages Per Session by Day in Week
        # daytotal = [0, 0, 0, 0, 0, 0, 0]
        # sql = "SELECT Date_dayinweek, pages_per_session FROM Summary_SessionAveragePagesPerSessionByDayInWeek WHERE DATE_WEEK = %d  AND course_id=%d ORDER BY Date_dayinweek;" % (
        # course_weeks[week_no - 1], course_id)
        # row_count = cursor.execute(sql);
        # result = cursor.fetchall()
        # for dayidx, row in enumerate(result):
        #     try:
        #         daytotal[int(row[0])] = int(row[1])
        #     except IndexError:
        #         print('Index Error')
        #
        # averagepagespersessionbydayinweek = ','.join(map(str, daytotal))
        #
        # histogram = generate_userbyweek_histogram(week_id, course_id)
        #
        # communication_types, assessment_types, communication_types_str, assessment_types_str = get_contenttypes(
        #     course_type)
        #
        # excluse_contentype_list = communication_types + assessment_types
        # excluse_contentype_str = ','.join("'{0}'".format(x) for x in excluse_contentype_list)
        #
        # # Top Content
        # sql = "SELECT SUM(F.pageview) AS Pageviews, F.page_id, P.title, F.module, F.action, F.url, P.order_no FROM dim_dates D LEFT JOIN fact_coursevisits F ON D.Id = F.Date_Id JOIN dim_pages P ON F.page_id=P.content_id  WHERE F.page_id!=0 AND F.module NOT IN (%s) AND D.Date_dayinweek IN (0,1,2,3,4,5,6) AND D.DATE_week IN (%s) AND F.course_id=%d GROUP BY F.page_id ORDER BY Pageviews DESC LIMIT 10;" % (
        # excluse_contentype_str, course_weeks[week_no - 1], course_id)
        # cursor.execute(sql);
        # topcontent_resultset = cursor.fetchall()
        # topcontent_table = ""
        # for row in topcontent_resultset:
        #     user_cnt = str(get_userweekcount(course_weeks[week_no - 1], int(row[1]), course_id, row[3], int(row[6])))
        #     topcontent_table = topcontent_table + '<tr><td><a href="/coursepage?page_id=%s&course_id=%s">%s</a></td><td class="center">%s</td><td class="center">%s</td><td class="center">%s</td></tr>' % (
        #     row[1], str(course_id), row[2], row[3], user_cnt, row[0])
        #
        # # Top Communcation Tools
        # topforumcontent_table = ""
        # sql = "SELECT SUM(F.pageview) AS Pageviews, F.page_id, P.title, F.module, F.action, F.url, P.order_no FROM dim_dates  D LEFT JOIN fact_coursevisits F ON D.Id = F.Date_Id JOIN dim_pages P ON F.page_id=P.content_id WHERE F.page_id!=0 AND F.module IN (%s) AND D.Date_dayinweek IN (0,1,2,3,4,5,6) AND D.DATE_week IN (%s) AND F.course_id=%d GROUP BY F.page_id ORDER BY Pageviews DESC LIMIT 10;" % (
        # communication_types_str, course_weeks[week_no - 1], course_id)
        # cursor.execute(sql);
        # topforumcontent_resultset = cursor.fetchall()
        # topforumcontent_table = ""
        # for row in topforumcontent_resultset:
        #     user_cnt = str(get_userweekcount(course_weeks[week_no - 1], int(row[1]), course_id, row[3], int(row[6])))
        #     no_posts = get_noforumposts(int(row[1]), course_id, course_weeks[week_no - 1])
        #     # no_participants = getusercount(3,1)
        #     topforumcontent_table = topforumcontent_table + '<tr><td><a href="/coursepage?page_id=%s&course_id=%s">%s</a></td><td class="center">%s</td><td class="center">%s</td><td class="center">%s</td><td class="center">%d</td></tr>' % (
        #     row[1], str(course_id), row[2], row[3], user_cnt, row[0], no_posts)
        #
        # # Top Assessment Items
        # sql = "SELECT SUM(F.pageview) AS Pageviews, F.page_id, P.title, F.module, F.action, F.url, P.order_no FROM dim_dates  D LEFT JOIN fact_coursevisits F ON D.Id = F.Date_Id JOIN dim_pages P ON F.page_id=P.content_id WHERE F.page_id!=0 AND F.module IN (%s) AND D.Date_dayinweek IN (0,1,2,3,4,5,6) AND D.DATE_week IN (%s) AND F.course_id=%d GROUP BY F.page_id ORDER BY Pageviews DESC LIMIT 10;" % (
        # assessment_types_str, course_weeks[week_no - 1], course_id)
        # cursor.execute(sql);
        # topquizcontent_resultset = cursor.fetchall()
        # topquizcontent_table = ""
        # for row in topquizcontent_resultset:
        #     user_cnt = str(get_quizusercount(course_weeks[week_no - 1], int(row[1]),
        #                                      course_id))  # str(get_userweekcount(course_weeks[week_no-1],int(row[1]),  course_id, row[3], int(row[6])))
        #     attempts = str(get_quizattemps(int(row[1]), course_id, unixstart=begweek_unix, unixend=endweek_unix))
        #     averagestudentscore = str(
        #         get_avggrade(int(row[1]), course_id, unixstart=begweek_unix, unixend=endweek_unix))
        #     topquizcontent_table = topquizcontent_table + '<tr><td><a href="/coursepage?page_id=%s&course_id=%s">%s</a></td><td class="center">%s</td><td class="center">%s</td><td class="center">%s</td><td class="center">%s</td></tr>' % (
        #     row[1], str(course_id), row[2], row[3], user_cnt, attempts, averagestudentscore)
        #
        # # Top Users/Students
        # sql = "SELECT COUNT(F.pageview) AS Pageviews, U.Firstname, U.Lastname, U.Role, F.user_id FROM dim_dates  D LEFT JOIN fact_coursevisits F ON D.Id = F.Date_Id JOIN dim_users U ON F.user_id=U.lms_id  WHERE D.DATE_week IN (%d) AND F.course_id=%d AND U.role='Student' GROUP BY F.user_id ORDER BY Pageviews DESC LIMIT 10;" % (
        # course_weeks[week_no - 1], course_id)
        # cursor.execute(sql);
        # topusers_resultset = cursor.fetchall()
        # topusers_table = ""
        # for row in topusers_resultset:
        #     topusers_table = topusers_table + '<tr><td class="center"><a href="/coursemember?user_id=%s_%s&course_id=%s">%s</a></td><td class="center">%s</td><td class="center">%s</td><td class="center">%s</td></tr>' % (
        #     str(course_id), row[4], str(course_id), row[1], row[2], row[3], row[0])
        #
        # # get repeating events
        # repeating_evt = CourseRepeatingEvent.objects.filter(course=course)
        # rpt_evt_lst = ""
        # for evt in repeating_evt:
        #     rpt_evt_lst = rpt_evt_lst + "{ value: %s, color: 'green', width: 2, label: { text: '%s'}}," % (
        #     evt.day_of_week, evt.title)

        # context_dict = {'repeatingevents': rpt_evt_lst, 'course_weeks': course_weeks, 'week_id': week_id,
        #                 'weekbeg': weekbeg, 'weekend': weekend, 'PageViewGraphContentList': PageViewGraphContentList,
        #                 'PageViewGraphCommunicationList': PageViewGraphCommunicationList,
        #                 'PageViewGraphAssessmentList': PageViewGraphAssessmentList,
        #                 'PageViewGraphUniqueViewsList': PageViewGraphUniqueViewsList,
        #                 'histogram_labels': histogram["labels"], 'histogram_values': histogram["values"],
        #                 'sessionsbydayinweek': averagepagespersessionbydayinweek,
        #                 'averagesessionlengthbydayinweek': averagesessionlengthbydayinweek,
        #                 'averagepagespersessionbydayinweek': averagepagespersessionbydayinweek,
        #                 'topusers_table': topusers_table, 'topcontent_table': topcontent_table,
        #                 'topforumcontent_table': topforumcontent_table, 'topquizcontent_table': topquizcontent_table,
        #                 'course_id': course_id, 'course_code': course_code, 'course_title': course_title,
        #                 'week_no': week_no, 'uniquepageviewsbydayinweek': uniquepageviewsbydayinweek,
        #                 'participantsbydayinweek': participantsbydayinweek}

        context['course_weeks'] = course_weeks
        context['week_id'] = self.week_id
        context['weekbeg'] = weekbeg
        context['weekend'] = weekend
        context['course'] = self.course
        context['week_no'] = week_no
        context['PageViewGraphContentList'] = PageViewGraphContentList

        return context
