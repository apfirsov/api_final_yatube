from datetime import datetime


def year(request):
    """Context function. Add current year var to context."""
    return {
        'year': datetime.today().year
    }
