Here’s the brief upgrade checklist:

| Area | What went wrong | Where to upgrade |
|---|---|---|
| Comment privacy | Comments can be accessed for pending/rejected posts if their ID is known. | [comment_view.py](<O:/Skill Shikshya/Django projects/blog_project/blog/views/comment_view.py:17>) — apply the same visibility rules as `PostView`. |
| Saved posts | Serializer does not return saved-record ID; typo `read_only_fileds`; unnecessary update endpoints. | [savedPost_serializer.py](<O:/Skill Shikshya/Django projects/blog_project/blog/serializers/savedPost_serializer.py:5>) and [savedPost_view.py](<O:/Skill Shikshya/Django projects/blog_project/blog/views/savedPost_view.py:6>). |
| Dashboard | Super-admin dashboard crashes because it uses `dict += dict`. | [admin_dashboard.py](<O:/Skill Shikshya/Django projects/blog_project/dashboard/views/admin_dashboard.py:26>) — use `.update()`. |
| Soft delete | Deleting sets `is_active=True`; deleted records are not automatically hidden. | [models.py](<O:/Skill Shikshya/Django projects/blog_project/base/models.py:4>) — set inactive and make the default manager exclude deleted rows. |
| Moderation | Two reviewers can approve/reject simultaneously; approved posts can potentially be rejected later. | [post_view.py](<O:/Skill Shikshya/Django projects/blog_project/blog/views/post_view.py:137>) — use transactions/row locking and allow transitions only from `pending`. |
| WebSocket auth | JWT is passed through URL query parameters, which may leak in logs/history. | [middleware.py](<O:/Skill Shikshya/Django projects/blog_project/notifications/middleware.py:26>) — move to safer authentication and validate WebSocket origins. |
| Notifications | Works, but notification creation and Redis sending happen in the request cycle; it will slow down with many reviewers. | [services.py](<O:/Skill Shikshya/Django projects/blog_project/notifications/services.py:40>) — later move delivery to Celery/RQ/outbox jobs. |
| Query efficiency | Posts prefetch comments unnecessarily; notifications likely query each post separately. | [post_view.py](<O:/Skill Shikshya/Django projects/blog_project/blog/views/post_view.py:23>) and [views.py](<O:/Skill Shikshya/Django projects/blog_project/notifications/views.py:6>). |
| Management API | `ModelViewSet` exposes routes such as update/create that do not match your intended role policy. | [user_management.py](<O:/Skill Shikshya/Django projects/blog_project/management/views/user_management.py:16>) — use only needed mixins/actions. |
| Moderator creation | Client can send a role value; backend overwrites it afterward. | [user_mgmt_serializer.py](<O:/Skill Shikshya/Django projects/blog_project/management/serializers/user_mgmt_serializer.py:16>) — do not accept `role`; set it server-side. |
| Media | Uploaded images are stored inside `static`, mixing deploy assets and user uploads. | [settings.py](<O:/Skill Shikshya/Django projects/blog_project/blog_project/settings.py:161>) — use a separate `media` directory/cloud storage. |
| API responses | Some endpoints use custom response envelopes and others use normal DRF responses. | Across views — standardize one API response format. |
| Tests | Most critical flows are not tested. | Add tests for permissions, moderation, comments, saved posts, notifications, management, and dashboard. |

Priority order: **comment visibility → saved posts → dashboard → soft delete → moderation concurrency → WebSocket security**.