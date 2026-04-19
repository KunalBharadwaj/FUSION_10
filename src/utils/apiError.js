export const getApiErrorMessage = (
  error,
  fallback = "Something went wrong. Please try again.",
) => {
  if (!error) {
    return fallback;
  }

  if (error.code === "ECONNABORTED") {
    return "Request timed out. Please try again.";
  }

  if (!error.response) {
    return error.message || "Network error. Please check your connection.";
  }

  const { status, data } = error.response;

  const payloadMessage =
    (typeof data === "string" && data) ||
    data?.error ||
    data?.message ||
    data?.detail;

  if (Array.isArray(payloadMessage)) {
    return payloadMessage.filter(Boolean).join(" ");
  }

  if (payloadMessage && typeof payloadMessage === "object") {
    const firstKey = Object.keys(payloadMessage)[0];
    const firstVal = payloadMessage[firstKey];
    if (Array.isArray(firstVal)) {
      return firstVal.filter(Boolean).join(" ");
    }
    if (firstVal) {
      return String(firstVal);
    }
  }

  if (payloadMessage) {
    return String(payloadMessage);
  }

  if (status === 400) {
    return "Invalid request. Please verify the form details.";
  }
  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }
  if (status === 403) {
    return "You do not have permission for this action.";
  }
  if (status === 404) {
    return "Requested resource was not found.";
  }
  if (status >= 500) {
    return "Server error. Please try again shortly.";
  }

  return fallback;
};
