//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'package:dio/dio.dart';
import 'package:built_value/serializer.dart';
import 'package:signupflow_api/src/serializers.dart';
import 'package:signupflow_api/src/auth/api_key_auth.dart';
import 'package:signupflow_api/src/auth/basic_auth.dart';
import 'package:signupflow_api/src/auth/bearer_auth.dart';
import 'package:signupflow_api/src/auth/oauth.dart';
import 'package:signupflow_api/src/api/analytics_api.dart';
import 'package:signupflow_api/src/api/assignments_api.dart';
import 'package:signupflow_api/src/api/audit_api.dart';
import 'package:signupflow_api/src/api/auth_api.dart';
import 'package:signupflow_api/src/api/availability_api.dart';
import 'package:signupflow_api/src/api/calendar_api.dart';
import 'package:signupflow_api/src/api/conflicts_api.dart';
import 'package:signupflow_api/src/api/constraints_api.dart';
import 'package:signupflow_api/src/api/events_api.dart';
import 'package:signupflow_api/src/api/health_api.dart';
import 'package:signupflow_api/src/api/holidays_api.dart';
import 'package:signupflow_api/src/api/invitations_api.dart';
import 'package:signupflow_api/src/api/organizations_api.dart';
import 'package:signupflow_api/src/api/people_api.dart';
import 'package:signupflow_api/src/api/recurring_events_api.dart';
import 'package:signupflow_api/src/api/resources_api.dart';
import 'package:signupflow_api/src/api/root_api.dart';
import 'package:signupflow_api/src/api/solutions_api.dart';
import 'package:signupflow_api/src/api/solver_api.dart';
import 'package:signupflow_api/src/api/teams_api.dart';

class SignupflowApi {
  static const String basePath = r'http://localhost';

  final Dio dio;
  final Serializers serializers;

  SignupflowApi({
    Dio? dio,
    Serializers? serializers,
    String? basePathOverride,
    List<Interceptor>? interceptors,
  })  : this.serializers = serializers ?? standardSerializers,
        this.dio = dio ??
            Dio(BaseOptions(
              baseUrl: basePathOverride ?? basePath,
              connectTimeout: const Duration(milliseconds: 5000),
              receiveTimeout: const Duration(milliseconds: 3000),
            )) {
    if (interceptors == null) {
      this.dio.interceptors.addAll([
        OAuthInterceptor(),
        BasicAuthInterceptor(),
        BearerAuthInterceptor(),
        ApiKeyAuthInterceptor(),
      ]);
    } else {
      this.dio.interceptors.addAll(interceptors);
    }
  }

  void setOAuthToken(String name, String token) {
    if (this.dio.interceptors.any((i) => i is OAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is OAuthInterceptor) as OAuthInterceptor).tokens[name] = token;
    }
  }

  void setBearerAuth(String name, String token) {
    if (this.dio.interceptors.any((i) => i is BearerAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is BearerAuthInterceptor) as BearerAuthInterceptor).tokens[name] = token;
    }
  }

  void setBasicAuth(String name, String username, String password) {
    if (this.dio.interceptors.any((i) => i is BasicAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((i) => i is BasicAuthInterceptor) as BasicAuthInterceptor).authInfo[name] = BasicAuthInfo(username, password);
    }
  }

  void setApiKey(String name, String apiKey) {
    if (this.dio.interceptors.any((i) => i is ApiKeyAuthInterceptor)) {
      (this.dio.interceptors.firstWhere((element) => element is ApiKeyAuthInterceptor) as ApiKeyAuthInterceptor).apiKeys[name] = apiKey;
    }
  }

  /// Get AnalyticsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AnalyticsApi getAnalyticsApi() {
    return AnalyticsApi(dio, serializers);
  }

  /// Get AssignmentsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AssignmentsApi getAssignmentsApi() {
    return AssignmentsApi(dio, serializers);
  }

  /// Get AuditApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AuditApi getAuditApi() {
    return AuditApi(dio, serializers);
  }

  /// Get AuthApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AuthApi getAuthApi() {
    return AuthApi(dio, serializers);
  }

  /// Get AvailabilityApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  AvailabilityApi getAvailabilityApi() {
    return AvailabilityApi(dio, serializers);
  }

  /// Get CalendarApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  CalendarApi getCalendarApi() {
    return CalendarApi(dio, serializers);
  }

  /// Get ConflictsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConflictsApi getConflictsApi() {
    return ConflictsApi(dio, serializers);
  }

  /// Get ConstraintsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ConstraintsApi getConstraintsApi() {
    return ConstraintsApi(dio, serializers);
  }

  /// Get EventsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  EventsApi getEventsApi() {
    return EventsApi(dio, serializers);
  }

  /// Get HealthApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  HealthApi getHealthApi() {
    return HealthApi(dio, serializers);
  }

  /// Get HolidaysApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  HolidaysApi getHolidaysApi() {
    return HolidaysApi(dio, serializers);
  }

  /// Get InvitationsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  InvitationsApi getInvitationsApi() {
    return InvitationsApi(dio, serializers);
  }

  /// Get OrganizationsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  OrganizationsApi getOrganizationsApi() {
    return OrganizationsApi(dio, serializers);
  }

  /// Get PeopleApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  PeopleApi getPeopleApi() {
    return PeopleApi(dio, serializers);
  }

  /// Get RecurringEventsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  RecurringEventsApi getRecurringEventsApi() {
    return RecurringEventsApi(dio, serializers);
  }

  /// Get ResourcesApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  ResourcesApi getResourcesApi() {
    return ResourcesApi(dio, serializers);
  }

  /// Get RootApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  RootApi getRootApi() {
    return RootApi(dio, serializers);
  }

  /// Get SolutionsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  SolutionsApi getSolutionsApi() {
    return SolutionsApi(dio, serializers);
  }

  /// Get SolverApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  SolverApi getSolverApi() {
    return SolverApi(dio, serializers);
  }

  /// Get TeamsApi instance, base route and serializer can be overridden by a given but be careful,
  /// by doing that all interceptors will not be executed
  TeamsApi getTeamsApi() {
    return TeamsApi(dio, serializers);
  }
}
