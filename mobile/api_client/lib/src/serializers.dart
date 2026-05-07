//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_import

import 'package:one_of_serializer/any_of_serializer.dart';
import 'package:one_of_serializer/one_of_serializer.dart';
import 'package:built_collection/built_collection.dart';
import 'package:built_value/json_object.dart';
import 'package:built_value/serializer.dart';
import 'package:built_value/standard_json_plugin.dart';
import 'package:built_value/iso_8601_date_time_serializer.dart';
import 'package:signupflow_api/src/date_serializer.dart';
import 'package:signupflow_api/src/model/date.dart';

import 'package:signupflow_api/src/model/assignment_change.dart';
import 'package:signupflow_api/src/model/assignment_decline_request.dart';
import 'package:signupflow_api/src/model/assignment_request.dart';
import 'package:signupflow_api/src/model/assignment_response.dart';
import 'package:signupflow_api/src/model/assignment_swap_request.dart';
import 'package:signupflow_api/src/model/audit_log_response.dart';
import 'package:signupflow_api/src/model/auth_response.dart';
import 'package:signupflow_api/src/model/available_person.dart';
import 'package:signupflow_api/src/model/bulk_import_item_error.dart';
import 'package:signupflow_api/src/model/bulk_import_response.dart';
import 'package:signupflow_api/src/model/calendar_subscription_response.dart';
import 'package:signupflow_api/src/model/calendar_token_reset_response.dart';
import 'package:signupflow_api/src/model/conflict_check_request.dart';
import 'package:signupflow_api/src/model/conflict_check_response.dart';
import 'package:signupflow_api/src/model/conflict_type.dart';
import 'package:signupflow_api/src/model/constraint_create.dart';
import 'package:signupflow_api/src/model/constraint_response.dart';
import 'package:signupflow_api/src/model/constraint_update.dart';
import 'package:signupflow_api/src/model/event_create.dart';
import 'package:signupflow_api/src/model/event_response.dart';
import 'package:signupflow_api/src/model/event_update.dart';
import 'package:signupflow_api/src/model/export_format.dart';
import 'package:signupflow_api/src/model/fairness_metrics.dart';
import 'package:signupflow_api/src/model/fairness_stats.dart';
import 'package:signupflow_api/src/model/http_validation_error.dart';
import 'package:signupflow_api/src/model/holiday_bulk_import.dart';
import 'package:signupflow_api/src/model/holiday_bulk_import_error.dart';
import 'package:signupflow_api/src/model/holiday_bulk_import_item.dart';
import 'package:signupflow_api/src/model/holiday_bulk_import_response.dart';
import 'package:signupflow_api/src/model/holiday_create.dart';
import 'package:signupflow_api/src/model/holiday_response.dart';
import 'package:signupflow_api/src/model/holiday_update.dart';
import 'package:signupflow_api/src/model/invitation_accept.dart';
import 'package:signupflow_api/src/model/invitation_accept_response.dart';
import 'package:signupflow_api/src/model/invitation_create.dart';
import 'package:signupflow_api/src/model/invitation_response.dart';
import 'package:signupflow_api/src/model/invitation_verify.dart';
import 'package:signupflow_api/src/model/list_response_assignment_response.dart';
import 'package:signupflow_api/src/model/list_response_audit_log_response.dart';
import 'package:signupflow_api/src/model/list_response_conflict_type.dart';
import 'package:signupflow_api/src/model/list_response_constraint_response.dart';
import 'package:signupflow_api/src/model/list_response_event_response.dart';
import 'package:signupflow_api/src/model/list_response_holiday_response.dart';
import 'package:signupflow_api/src/model/list_response_invitation_response.dart';
import 'package:signupflow_api/src/model/list_response_organization_response.dart';
import 'package:signupflow_api/src/model/list_response_person_response.dart';
import 'package:signupflow_api/src/model/list_response_recurring_series_response.dart';
import 'package:signupflow_api/src/model/list_response_resource_response.dart';
import 'package:signupflow_api/src/model/list_response_solution_response.dart';
import 'package:signupflow_api/src/model/list_response_team_response.dart';
import 'package:signupflow_api/src/model/login_request.dart';
import 'package:signupflow_api/src/model/occurrence_preview.dart';
import 'package:signupflow_api/src/model/organization_create.dart';
import 'package:signupflow_api/src/model/organization_response.dart';
import 'package:signupflow_api/src/model/organization_update.dart';
import 'package:signupflow_api/src/model/password_reset_confirm.dart';
import 'package:signupflow_api/src/model/password_reset_request.dart';
import 'package:signupflow_api/src/model/person_create.dart';
import 'package:signupflow_api/src/model/person_response.dart';
import 'package:signupflow_api/src/model/person_update.dart';
import 'package:signupflow_api/src/model/preview_request.dart';
import 'package:signupflow_api/src/model/recurring_series_create.dart';
import 'package:signupflow_api/src/model/recurring_series_response.dart';
import 'package:signupflow_api/src/model/resource_create.dart';
import 'package:signupflow_api/src/model/resource_response.dart';
import 'package:signupflow_api/src/model/resource_update.dart';
import 'package:signupflow_api/src/model/signup_request.dart';
import 'package:signupflow_api/src/model/solution_diff_response.dart';
import 'package:signupflow_api/src/model/solution_metrics.dart';
import 'package:signupflow_api/src/model/solution_response.dart';
import 'package:signupflow_api/src/model/solution_stats_response.dart';
import 'package:signupflow_api/src/model/solve_request.dart';
import 'package:signupflow_api/src/model/solve_response.dart';
import 'package:signupflow_api/src/model/stability_metrics.dart';
import 'package:signupflow_api/src/model/team_create.dart';
import 'package:signupflow_api/src/model/team_member_add.dart';
import 'package:signupflow_api/src/model/team_member_remove.dart';
import 'package:signupflow_api/src/model/team_response.dart';
import 'package:signupflow_api/src/model/team_update.dart';
import 'package:signupflow_api/src/model/time_off_create.dart';
import 'package:signupflow_api/src/model/validation_error.dart';
import 'package:signupflow_api/src/model/validation_error_loc_inner.dart';
import 'package:signupflow_api/src/model/violation_info.dart';
import 'package:signupflow_api/src/model/workload_stats.dart';

part 'serializers.g.dart';

@SerializersFor([
  AssignmentChange,
  AssignmentDeclineRequest,
  AssignmentRequest,
  AssignmentResponse,
  AssignmentSwapRequest,
  AuditLogResponse,
  AuthResponse,
  AvailablePerson,
  BulkImportItemError,
  BulkImportResponse,
  CalendarSubscriptionResponse,
  CalendarTokenResetResponse,
  ConflictCheckRequest,
  ConflictCheckResponse,
  ConflictType,
  ConstraintCreate,
  ConstraintResponse,
  ConstraintUpdate,
  EventCreate,
  EventResponse,
  EventUpdate,
  ExportFormat,
  FairnessMetrics,
  FairnessStats,
  HTTPValidationError,
  HolidayBulkImport,
  HolidayBulkImportError,
  HolidayBulkImportItem,
  HolidayBulkImportResponse,
  HolidayCreate,
  HolidayResponse,
  HolidayUpdate,
  InvitationAccept,
  InvitationAcceptResponse,
  InvitationCreate,
  InvitationResponse,
  InvitationVerify,
  ListResponseAssignmentResponse,
  ListResponseAuditLogResponse,
  ListResponseConflictType,
  ListResponseConstraintResponse,
  ListResponseEventResponse,
  ListResponseHolidayResponse,
  ListResponseInvitationResponse,
  ListResponseOrganizationResponse,
  ListResponsePersonResponse,
  ListResponseRecurringSeriesResponse,
  ListResponseResourceResponse,
  ListResponseSolutionResponse,
  ListResponseTeamResponse,
  LoginRequest,
  OccurrencePreview,
  OrganizationCreate,
  OrganizationResponse,
  OrganizationUpdate,
  PasswordResetConfirm,
  PasswordResetRequest,
  PersonCreate,
  PersonResponse,
  PersonUpdate,
  PreviewRequest,
  RecurringSeriesCreate,
  RecurringSeriesResponse,
  ResourceCreate,
  ResourceResponse,
  ResourceUpdate,
  SignupRequest,
  SolutionDiffResponse,
  SolutionMetrics,
  SolutionResponse,
  SolutionStatsResponse,
  SolveRequest,
  SolveResponse,
  StabilityMetrics,
  TeamCreate,
  TeamMemberAdd,
  TeamMemberRemove,
  TeamResponse,
  TeamUpdate,
  TimeOffCreate,
  ValidationError,
  ValidationErrorLocInner,
  ViolationInfo,
  WorkloadStats,
])
Serializers serializers = (_$serializers.toBuilder()
      ..addBuilderFactory(
        const FullType(BuiltList, [FullType(OccurrencePreview)]),
        () => ListBuilder<OccurrencePreview>(),
      )
      ..addBuilderFactory(
        const FullType(BuiltList, [FullType(AvailablePerson)]),
        () => ListBuilder<AvailablePerson>(),
      )
      ..addBuilderFactory(
        const FullType(BuiltMap, [FullType(String), FullType.nullable(JsonObject)]),
        () => MapBuilder<String, JsonObject>(),
      )
      ..addBuilderFactory(
        const FullType(BuiltMap, [FullType(String), FullType(JsonObject)]),
        () => MapBuilder<String, JsonObject>(),
      )
      ..add(const OneOfSerializer())
      ..add(const AnyOfSerializer())
      ..add(const DateSerializer())
      ..add(Iso8601DateTimeSerializer())
    ).build();

Serializers standardSerializers =
    (serializers.toBuilder()..addPlugin(StandardJsonPlugin())).build();
