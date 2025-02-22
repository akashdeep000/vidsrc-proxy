var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "http",
        host: "brd.superproxy.io",
        port: parseInt("33335")
      },
    bypassList: [""]
    }
  };
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
    return {
        authCredentials: {
            username: "brd-customer-hl_ef2cdf28-zone-datacenter_proxy2",
            password: "ktt16ru4d08y"
        }
    };
}
chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
);