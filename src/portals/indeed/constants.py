"""Constantes de Indeed: la API GraphQL que usa su app de iPhone."""

GRAPHQL_URL = "https://apis.indeed.com/graphql"

JOB_URL = "https://ar.indeed.com/viewjob?jk={job_id}"

HEADERS = {
    "indeed-api-key": "161092c2017b5bbab13edb12461a62d5a833871e7cad6d9d475304573de67ac8",
    "user-agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Indeed App 193.1"
    ),
    "indeed-app-info": "appv=193.1; appid=com.indeed.jobsearch; osv=16.6.1; os=ios; dtype=phone",
    "indeed-co": "AR",
    "indeed-locale": "es-AR",
    "accept": "application/json",
}

JOBS_PER_PAGE = 100

RADIUS = 50

QUERY = """
query {{
  jobSearch(
    what: {what}
    location: {{where: {where}, radius: {radius}, radiusUnit: MILES}}
    limit: {limit}
    {cursor}
    sort: DATE
    filters: [{{ date: {{ field: "dateOnIndeed", start: "{hours}h" }} }}]
  ) {{
    pageInfo {{ nextCursor }}
    results {{ job {{ key title description {{ html }} }} }}
  }}
}}
"""
