// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'serializers.dart';

// **************************************************************************
// BuiltValueGenerator
// **************************************************************************

Serializers _$serializers = (Serializers().toBuilder()
      ..add(AssignmentChange.serializer)
      ..add(AssignmentDeclineRequest.serializer)
      ..add(AssignmentRequest.serializer)
      ..add(AssignmentResponse.serializer)
      ..add(AssignmentSwapRequest.serializer)
      ..add(AuditLogResponse.serializer)
      ..add(AuthResponse.serializer)
      ..add(AvailablePerson.serializer)
      ..add(BulkImportItemError.serializer)
      ..add(BulkImportResponse.serializer)
      ..add(CalendarSubscriptionResponse.serializer)
      ..add(CalendarTokenResetResponse.serializer)
      ..add(ConflictCheckRequest.serializer)
      ..add(ConflictCheckResponse.serializer)
      ..add(ConflictType.serializer)
      ..add(ConstraintCreate.serializer)
      ..add(ConstraintResponse.serializer)
      ..add(ConstraintUpdate.serializer)
      ..add(EventCreate.serializer)
      ..add(EventResponse.serializer)
      ..add(EventUpdate.serializer)
      ..add(ExportFormat.serializer)
      ..add(FairnessMetrics.serializer)
      ..add(FairnessStats.serializer)
      ..add(HTTPValidationError.serializer)
      ..add(HolidayBulkImport.serializer)
      ..add(HolidayBulkImportError.serializer)
      ..add(HolidayBulkImportItem.serializer)
      ..add(HolidayBulkImportResponse.serializer)
      ..add(HolidayCreate.serializer)
      ..add(HolidayResponse.serializer)
      ..add(HolidayUpdate.serializer)
      ..add(InvitationAccept.serializer)
      ..add(InvitationAcceptResponse.serializer)
      ..add(InvitationCreate.serializer)
      ..add(InvitationResponse.serializer)
      ..add(InvitationVerify.serializer)
      ..add(ListResponseAssignmentResponse.serializer)
      ..add(ListResponseAuditLogResponse.serializer)
      ..add(ListResponseConflictType.serializer)
      ..add(ListResponseConstraintResponse.serializer)
      ..add(ListResponseEventResponse.serializer)
      ..add(ListResponseHolidayResponse.serializer)
      ..add(ListResponseInvitationResponse.serializer)
      ..add(ListResponseOrganizationResponse.serializer)
      ..add(ListResponsePersonResponse.serializer)
      ..add(ListResponseRecurringSeriesResponse.serializer)
      ..add(ListResponseResourceResponse.serializer)
      ..add(ListResponseSolutionResponse.serializer)
      ..add(ListResponseTeamResponse.serializer)
      ..add(LoginRequest.serializer)
      ..add(OccurrencePreview.serializer)
      ..add(OrganizationCreate.serializer)
      ..add(OrganizationResponse.serializer)
      ..add(OrganizationUpdate.serializer)
      ..add(PasswordResetConfirm.serializer)
      ..add(PasswordResetRequest.serializer)
      ..add(PersonCreate.serializer)
      ..add(PersonResponse.serializer)
      ..add(PersonUpdate.serializer)
      ..add(PreviewRequest.serializer)
      ..add(RecurringSeriesCreate.serializer)
      ..add(RecurringSeriesResponse.serializer)
      ..add(ResourceCreate.serializer)
      ..add(ResourceResponse.serializer)
      ..add(ResourceUpdate.serializer)
      ..add(SignupRequest.serializer)
      ..add(SolutionDiffResponse.serializer)
      ..add(SolutionMetrics.serializer)
      ..add(SolutionResponse.serializer)
      ..add(SolutionStatsResponse.serializer)
      ..add(SolveRequest.serializer)
      ..add(SolveResponse.serializer)
      ..add(StabilityMetrics.serializer)
      ..add(TeamCreate.serializer)
      ..add(TeamMemberAdd.serializer)
      ..add(TeamMemberRemove.serializer)
      ..add(TeamResponse.serializer)
      ..add(TeamUpdate.serializer)
      ..add(TimeOffCreate.serializer)
      ..add(ValidationError.serializer)
      ..add(ValidationErrorLocInner.serializer)
      ..add(ViolationInfo.serializer)
      ..add(WorkloadStats.serializer)
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(AssignmentChange)]),
          () => ListBuilder<AssignmentChange>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(AssignmentChange)]),
          () => ListBuilder<AssignmentChange>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(AssignmentResponse)]),
          () => ListBuilder<AssignmentResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(AuditLogResponse)]),
          () => ListBuilder<AuditLogResponse>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(BulkImportItemError)]),
          () => ListBuilder<BulkImportItemError>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ConflictType)]),
          () => ListBuilder<ConflictType>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ConflictType)]),
          () => ListBuilder<ConflictType>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ConstraintResponse)]),
          () => ListBuilder<ConstraintResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(EventResponse)]),
          () => ListBuilder<EventResponse>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(HolidayBulkImportError)]),
          () => ListBuilder<HolidayBulkImportError>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(HolidayBulkImportItem)]),
          () => ListBuilder<HolidayBulkImportItem>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(HolidayResponse)]),
          () => ListBuilder<HolidayResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(InvitationResponse)]),
          () => ListBuilder<InvitationResponse>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(OrganizationResponse)]),
          () => ListBuilder<OrganizationResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(PersonResponse)]),
          () => ListBuilder<PersonResponse>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(RecurringSeriesResponse)]),
          () => ListBuilder<RecurringSeriesResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ResourceResponse)]),
          () => ListBuilder<ResourceResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(SolutionResponse)]),
          () => ListBuilder<SolutionResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(TeamResponse)]),
          () => ListBuilder<TeamResponse>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ValidationError)]),
          () => ListBuilder<ValidationError>())
      ..addBuilderFactory(
          const FullType(
              BuiltList, const [const FullType(ValidationErrorLocInner)]),
          () => ListBuilder<ValidationErrorLocInner>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(ViolationInfo)]),
          () => ListBuilder<ViolationInfo>())
      ..addBuilderFactory(
          const FullType(
              BuiltMap, const [const FullType(String), const FullType(int)]),
          () => MapBuilder<String, int>())
      ..addBuilderFactory(
          const FullType(
              BuiltMap, const [const FullType(String), const FullType(int)]),
          () => MapBuilder<String, int>())
      ..addBuilderFactory(
          const FullType(
              BuiltMap, const [const FullType(String), const FullType(int)]),
          () => MapBuilder<String, int>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>())
      ..addBuilderFactory(
          const FullType(BuiltMap, const [
            const FullType(String),
            const FullType.nullable(JsonObject)
          ]),
          () => MapBuilder<String, JsonObject?>())
      ..addBuilderFactory(
          const FullType(BuiltList, const [const FullType(String)]),
          () => ListBuilder<String>()))
    .build();

// ignore_for_file: deprecated_member_use_from_same_package,type=lint
