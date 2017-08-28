def constants(request):
    return {
        'BASE_URL': request.build_absolute_uri('/'),
        'BASE_API_URL': request.build_absolute_uri('/api/'),
    }
