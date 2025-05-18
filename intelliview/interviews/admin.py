from django.contrib import admin
from .models import InterviewSession, InterviewHistoryData

class InterviewHistoryDataInline(admin.TabularInline):
    model = InterviewHistoryData
    extra = 0
    readonly_fields = ['question_text', 'answer_text', 'feedback', 'score']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'started_at', 'completed', 'score']
    list_filter = ['completed', 'started_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['started_at']
    inlines = [InterviewHistoryDataInline]
    
@admin.register(InterviewHistoryData)
class InterviewHistoryDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'score', 'created_at']
    list_filter = ['session__completed']
    search_fields = ['question_text', 'answer_text', 'feedback']
    readonly_fields = ['created_at'] 