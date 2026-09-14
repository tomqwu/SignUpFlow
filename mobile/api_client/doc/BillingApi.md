# signupflow_api.api.BillingApi

## Load the API package
```dart
import 'package:signupflow_api/api.dart';
```

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**addPaymentMethod**](BillingApi.md#addpaymentmethod) | **POST** /api/v1/billing/payment-methods | Add Payment Method
[**cancelDowngrade**](BillingApi.md#canceldowngrade) | **POST** /api/v1/billing/subscription/cancel-downgrade | Cancel Downgrade
[**cancelSubscription**](BillingApi.md#cancelsubscription) | **POST** /api/v1/billing/subscription/cancel | Cancel Subscription
[**createBillingPortalSession**](BillingApi.md#createbillingportalsession) | **POST** /api/v1/billing/portal | Create Billing Portal Session
[**downgradeSubscription**](BillingApi.md#downgradesubscription) | **POST** /api/v1/billing/subscription/downgrade | Downgrade Subscription
[**downloadInvoicePdf**](BillingApi.md#downloadinvoicepdf) | **GET** /api/v1/billing/invoices/{billing_history_id}/pdf | Download Invoice Pdf
[**getBillingHistory**](BillingApi.md#getbillinghistory) | **GET** /api/v1/billing/history | Get Billing History
[**getPaymentMethods**](BillingApi.md#getpaymentmethods) | **GET** /api/v1/billing/payment-methods | Get Payment Methods
[**getSubscription**](BillingApi.md#getsubscription) | **GET** /api/v1/billing/subscription | Get Subscription
[**handleCheckoutSuccess**](BillingApi.md#handlecheckoutsuccess) | **POST** /api/v1/billing/subscription/checkout-success | Handle Checkout Success
[**reactivateSubscription**](BillingApi.md#reactivatesubscription) | **POST** /api/v1/billing/subscription/reactivate | Reactivate Subscription
[**removePaymentMethod**](BillingApi.md#removepaymentmethod) | **DELETE** /api/v1/billing/payment-methods/{payment_method_id} | Remove Payment Method
[**setPrimaryPaymentMethod**](BillingApi.md#setprimarypaymentmethod) | **PUT** /api/v1/billing/payment-methods/{payment_method_id}/primary | Set Primary Payment Method
[**startTrial**](BillingApi.md#starttrial) | **POST** /api/v1/billing/subscription/trial | Start Trial
[**upgradeSubscription**](BillingApi.md#upgradesubscription) | **POST** /api/v1/billing/subscription/upgrade | Upgrade Subscription


# **addPaymentMethod**
> BuiltMap<String, JsonObject> addPaymentMethod(paymentMethodId, orgId)

Add Payment Method

Add new payment method to organization via Stripe.  Payment method must be created client-side using Stripe.js before calling this endpoint.  Requires:     - User must be admin     - User must belong to the organization  Query Parameters:     payment_method_id: Stripe payment method ID (created client-side)     org_id: Organization ID  Returns:     {         \"success\": true,         \"message\": \"Payment method added successfully\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String paymentMethodId = paymentMethodId_example; // String | Stripe payment method ID
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.addPaymentMethod(paymentMethodId, orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->addPaymentMethod: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **paymentMethodId** | **String**| Stripe payment method ID |
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancelDowngrade**
> BuiltMap<String, JsonObject> cancelDowngrade(orgId)

Cancel Downgrade

Cancel scheduled downgrade.  This endpoint: 1. Verifies pending downgrade exists 2. Clears pending_downgrade field from subscription 3. Records subscription event for audit trail  Requires:     - User must be admin     - User must belong to the organization     - Organization must have pending downgrade scheduled  Returns:     dict: Cancellation confirmation     {         \"success\": true,         \"subscription\": SubscriptionResponse,         \"message\": \"Downgrade cancelled\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.cancelDowngrade(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->cancelDowngrade: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancelSubscription**
> BuiltMap<String, JsonObject> cancelSubscription(cancelRequest)

Cancel Subscription

Cancel subscription with service continuing until period end.  This endpoint: 1. Cancels subscription in Stripe (at period end by default) 2. Service continues until current period ends 3. Organization downgraded to Free plan at period end 4. Data retained for 30 days after cancellation 5. Records cancellation event for audit trail 6. Sends cancellation confirmation email (future)  Requires:     - User must be admin     - User must belong to the organization     - Organization must have active paid subscription  Request Body:     {         \"org_id\": \"org_123\",         \"immediately\": false,         \"reason\": \"Cost reduction\",         \"feedback\": \"Great service, just downsizing\"     }  Returns:     dict: Cancellation details     {         \"success\": true,         \"subscription\": SubscriptionResponse,         \"period_end\": \"2025-11-23T...\",         \"data_retention_until\": \"2025-12-23T...\",         \"message\": \"Subscription will cancel at period end\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final CancelRequest cancelRequest = ; // CancelRequest |

try {
    final response = api.cancelSubscription(cancelRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->cancelSubscription: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cancelRequest** | [**CancelRequest**](CancelRequest.md)|  |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createBillingPortalSession**
> BuiltMap<String, JsonObject> createBillingPortalSession(orgId)

Create Billing Portal Session

Create Stripe billing portal session for self-service management.  The Stripe billing portal allows customers to: - Update payment methods - View invoices and payment history - Update billing email - Cancel subscription  Requires:     - User must be admin of the organization     - Organization must have Stripe customer ID  Args:     org_id: Organization ID     return_url: URL to return to after portal session (from request body)  Returns:     dict: {\"success\": bool, \"url\": str}

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.createBillingPortalSession(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->createBillingPortalSession: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **downgradeSubscription**
> BuiltMap<String, JsonObject> downgradeSubscription(downgradeRequest)

Downgrade Subscription

Schedule subscription downgrade to execute at period end.  This endpoint: 1. Validates downgrade is to lower tier 2. Schedules downgrade for current period end 3. Calculates credit for unused time 4. Stores pending downgrade in subscription.pending_downgrade 5. Records subscription event for audit trail 6. Sends downgrade confirmation email (future)  Requires:     - User must be admin     - User must belong to the organization     - Organization must have active paid subscription     - New plan tier must be lower than current tier  Request Body:     {         \"org_id\": \"org_123\",         \"new_plan_tier\": \"starter\",         \"reason\": \"Cost reduction\"     }  Returns:     dict: Downgrade scheduled details     {         \"success\": true,         \"subscription\": SubscriptionResponse,         \"pending_downgrade\": {             \"new_plan_tier\": \"starter\",             \"effective_date\": \"2025-11-23\",             \"credit_amount_cents\": 5000,             \"reason\": \"Cost reduction\"         },         \"message\": \"Downgrade scheduled for end of billing period\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final DowngradeRequest downgradeRequest = ; // DowngradeRequest |

try {
    final response = api.downgradeSubscription(downgradeRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->downgradeSubscription: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **downgradeRequest** | [**DowngradeRequest**](DowngradeRequest.md)|  |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **downloadInvoicePdf**
> JsonObject downloadInvoicePdf(billingHistoryId, format)

Download Invoice Pdf

Generate and download invoice PDF for billing history record.  Returns PDF file for download or HTML preview.  Requires:     - User must be an authenticated admin of the organization  Path Parameters:     billing_history_id: Billing history record ID  Query Parameters:     format: Output format - \"pdf\" (text-based) or \"html\" (styled template)  Returns:     PDF file download or HTML response

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String billingHistoryId = billingHistoryId_example; // String |
final String format = format_example; // String | Output format (pdf or html)

try {
    final response = api.downloadInvoicePdf(billingHistoryId, format);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->downloadInvoicePdf: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **billingHistoryId** | **String**|  |
 **format** | **String**| Output format (pdf or html) | [optional] [default to 'html']

### Return type

[**JsonObject**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getBillingHistory**
> BuiltMap<String, JsonObject> getBillingHistory(orgId, page, limit)

Get Billing History

Get organization's billing history with pagination.  Returns list of billing events (charges, refunds, subscription changes).  Requires:     - User must be an authenticated admin of the organization  Query Parameters:     org_id: Organization ID     page: Page number (default: 1)     limit: Records per page (default: 50, max: 100)  Returns:     {         \"success\": true,         \"history\": [             {                 \"id\": 123,                 \"event_type\": \"charge\",                 \"amount_cents\": 2900,                 \"currency\": \"usd\",                 \"payment_status\": \"succeeded\",                 \"event_timestamp\": \"2025-10-23T10:00:00Z\",                 \"description\": \"Payment for starter plan\",                 \"stripe_invoice_id\": \"in_xxx\"             }         ],         \"pagination\": {             \"page\": 1,             \"limit\": 50,             \"total\": 45,             \"pages\": 1         }     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String orgId = orgId_example; // String | Organization ID
final int page = 56; // int | Page number (1-indexed)
final int limit = 56; // int | Records per page (default: 50)

try {
    final response = api.getBillingHistory(orgId, page, limit);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->getBillingHistory: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID |
 **page** | **int**| Page number (1-indexed) | [optional] [default to 1]
 **limit** | **int**| Records per page (default: 50) | [optional] [default to 50]

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPaymentMethods**
> BuiltMap<String, JsonObject> getPaymentMethods(orgId)

Get Payment Methods

Get organization's payment methods from Stripe.  Returns list of payment methods with card details, expiration, and primary status.  Requires:     - User must be an authenticated admin of the organization  Query Parameters:     org_id: Organization ID  Returns:     {         \"success\": true,         \"payment_methods\": [             {                 \"id\": \"pm_xxx\",                 \"type\": \"card\",                 \"card\": {                     \"brand\": \"visa\",                     \"last4\": \"4242\",                     \"exp_month\": 12,                     \"exp_year\": 2025                 },                 \"is_default\": true             }         ]     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.getPaymentMethods(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->getPaymentMethods: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSubscription**
> BuiltMap<String, JsonObject> getSubscription(orgId)

Get Subscription

Get current subscription details for organization.  Returns subscription tier, usage metrics, and billing information.  Requires:     - User must be an authenticated admin of the organization  Returns:     dict: Subscription details with usage metrics     {         \"subscription\": SubscriptionResponse,         \"usage\": UsageSummaryResponse,         \"next_invoice\": Optional[dict]     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.getSubscription(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->getSubscription: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **handleCheckoutSuccess**
> BuiltMap<String, JsonObject> handleCheckoutSuccess(sessionId)

Handle Checkout Success

Handle successful checkout completion.  This is called when user returns from Stripe checkout page after successful payment. The actual subscription update happens via webhook, but this endpoint can be used to retrieve updated subscription status.  Requires:     - User must be admin     - Valid Stripe session ID  Returns:     dict: Updated subscription details

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String sessionId = sessionId_example; // String | Stripe checkout session ID

try {
    final response = api.handleCheckoutSuccess(sessionId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->handleCheckoutSuccess: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sessionId** | **String**| Stripe checkout session ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reactivateSubscription**
> BuiltMap<String, JsonObject> reactivateSubscription(orgId)

Reactivate Subscription

Reactivate a cancelled subscription within data retention period.  This endpoint: 1. Validates organization is within 30-day retention window 2. Restores subscription to previous plan tier 3. Clears cancellation and retention timestamps 4. Records reactivation event for audit trail 5. Sends reactivation confirmation email (future)  Requires:     - User must be admin     - User must belong to the organization     - Organization must be within data retention period     - Subscription must be cancelled  Query Parameters:     org_id: Organization ID  Returns:     dict: Reactivation confirmation     {         \"success\": true,         \"subscription\": SubscriptionResponse,         \"usage\": UsageSummaryResponse,         \"message\": \"Subscription reactivated successfully...\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.reactivateSubscription(orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->reactivateSubscription: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **removePaymentMethod**
> BuiltMap<String, JsonObject> removePaymentMethod(paymentMethodId, orgId)

Remove Payment Method

Remove payment method from organization.  Requires:     - User must be admin     - User must belong to the organization     - Cannot remove the only payment method on active paid subscription  Path Parameters:     payment_method_id: Stripe payment method ID to remove  Query Parameters:     org_id: Organization ID  Returns:     {         \"success\": true,         \"message\": \"Payment method removed successfully\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String paymentMethodId = paymentMethodId_example; // String |
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.removePaymentMethod(paymentMethodId, orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->removePaymentMethod: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **paymentMethodId** | **String**|  |
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **setPrimaryPaymentMethod**
> BuiltMap<String, JsonObject> setPrimaryPaymentMethod(paymentMethodId, orgId)

Set Primary Payment Method

Set payment method as primary (default) for organization.  Requires:     - User must be admin     - User must belong to the organization  Path Parameters:     payment_method_id: Stripe payment method ID to set as primary  Query Parameters:     org_id: Organization ID  Returns:     {         \"success\": true,         \"message\": \"Primary payment method updated successfully\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final String paymentMethodId = paymentMethodId_example; // String |
final String orgId = orgId_example; // String | Organization ID

try {
    final response = api.setPrimaryPaymentMethod(paymentMethodId, orgId);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->setPrimaryPaymentMethod: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **paymentMethodId** | **String**|  |
 **orgId** | **String**| Organization ID |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **startTrial**
> BuiltMap<String, JsonObject> startTrial(trialRequest)

Start Trial

Start a 14-day trial of a paid plan.  This endpoint: 1. Validates organization is on free plan 2. Updates subscription to trial status 3. Sets trial_end_date to 14 days from now 4. Updates usage limits to trial plan tier 5. Records subscription event for audit trail 6. Sends trial welcome email (future)  Requires:     - User must be admin     - User must belong to the organization     - Organization must have active free plan  Request Body:     {         \"org_id\": \"org_123\",         \"plan_tier\": \"starter\",         \"trial_days\": 14     }  Returns:     dict: Trial subscription details     {         \"success\": true,         \"subscription\": SubscriptionResponse,         \"trial_end_date\": \"2025-11-06T...\",         \"message\": \"Started 14-day trial of starter plan\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final TrialRequest trialRequest = ; // TrialRequest |

try {
    final response = api.startTrial(trialRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->startTrial: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **trialRequest** | [**TrialRequest**](TrialRequest.md)|  |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upgradeSubscription**
> BuiltMap<String, JsonObject> upgradeSubscription(upgradeRequest)

Upgrade Subscription

Upgrade organization to paid plan.  This endpoint: 1. Creates Stripe checkout session for payment collection 2. Upgrades subscription when payment succeeds 3. Records billing history and audit trail 4. Updates usage limits to new plan tier 5. Sends confirmation email (future)  Requires:     - User must be admin     - User must belong to the organization     - Organization must have active free plan  Request Body:     {         \"org_id\": \"org_123\",         \"plan_tier\": \"starter\",         \"billing_cycle\": \"monthly\",         \"payment_method_id\": \"pm_xxx\",         \"trial_days\": 14     }  Returns:     dict: Checkout session URL for payment     {         \"success\": true,         \"checkout_url\": \"https://checkout.stripe.com/...\",         \"session_id\": \"cs_xxx\",         \"message\": \"Checkout session created\"     }

### Example
```dart
import 'package:signupflow_api/api.dart';

final api = SignupflowApi().getBillingApi();
final UpgradeRequest upgradeRequest = ; // UpgradeRequest |

try {
    final response = api.upgradeSubscription(upgradeRequest);
    print(response);
} catch on DioException (e) {
    print('Exception when calling BillingApi->upgradeSubscription: $e\n');
}
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upgradeRequest** | [**UpgradeRequest**](UpgradeRequest.md)|  |

### Return type

[**BuiltMap&lt;String, JsonObject&gt;**](JsonObject.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
