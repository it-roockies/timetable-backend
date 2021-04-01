from datetime import datetime, date, timedelta
from rest_framework.filters import BaseFilterBackend


class BookingWeekFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        week = request.query_params.get('week', 'current')

        if week == 'current':
            tomorrow = date.today() + timedelta(days=1)
            start_date = tomorrow - timedelta(days=tomorrow.weekday())
            end_date = start_date + timedelta(days=6)
            return queryset.filter(date__range = [start_date, end_date])

        start_date = datetime.strptime(f"{week}-1", "%Y-W%W-%w").date()
        end_date = start + timedelta(days=7)
        return queryset.filter(date__range=[start_date, end_date])

    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name="week",
                required=False,
                location='query',
                schema=coreschema.String(
                    title="Week",
                    description="Week number in format like e.g. 2021-W12"
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': "week",
                'required': False,
                'in': 'query',
                'description': "Week number in format like e.g. 2021-W12",
                'schema': {
                    'type': 'string',
                },
            },
        ]