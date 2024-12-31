resource "oci_identity_domains_dynamic_resource_group" "search-fn-dyngroup" {
    #Required
    provider       = oci.home    
    display_name = "${var.prefix}-fn-dyngroup"
    idcs_endpoint = local.idcs_url
    matching_rule = "ALL {resource.type = 'fnfunc', resource.compartment.id = '${local.lz_app_cmp_ocid}'}"
    schemas = ["urn:ietf:params:scim:schemas:oracle:idcs:DynamicResourceGroup"]
}

resource "oci_identity_domains_dynamic_resource_group" "search-bastion-dyngroup" {
    #Required
    provider       = oci.home    
    display_name = "${var.prefix}-bastion-dyngroup"
    idcs_endpoint = local.idcs_url
    matching_rule = "ALL {instance.id = '${oci_core_instance.starter_bastion.id}'}"
    schemas = ["urn:ietf:params:scim:schemas:oracle:idcs:DynamicResourceGroup"]
}

resource "time_sleep" "wait_30_seconds" {
  depends_on = [ oci_identity_domains_dynamic_resource_group.search-bastion-dyngroup, oci_identity_domains_dynamic_resource_group.search-fn-dyngroup ]
  create_duration = "30s"
}

resource "oci_identity_policy" "starter_search_policy" {
    provider       = oci.home    
    depends_on     = [ time_sleep.wait_30_seconds ]
    name           = "${var.prefix}-policy"
    description    = "${var.prefix} policy"
    compartment_id = local.lz_serv_cmp_ocid

    statements = [
        "allow dynamic-group ${var.idcs_domain_name}/${var.prefix}-fn-dyngroup to manage objects in compartment id ${local.lz_serv_cmp_ocid}",
        "allow dynamic-group ${var.idcs_domain_name}/${var.prefix}-bastion-dyngroup to manage all-resources in compartment id ${local.lz_serv_cmp_ocid}",
        "allow dynamic-group ${var.idcs_domain_name}/${var.prefix}-bastion-dyngroup to manage stream-family in compartment id ${local.lz_serv_cmp_ocid}",
        "allow dynamic-group ${var.idcs_domain_name}/${var.prefix}-bastion-dyngroup to manage genai-agent-family in compartment id ${local.lz_serv_cmp_ocid}",
        "allow any-user to manage genai-agent-family in compartment id ${local.lz_serv_cmp_ocid} where request.principal.id='${data.oci_database_autonomous_database.starter_atp.autonomous_database_id}'",
        "allow any-user to read object-family in compartment id ${local.lz_serv_cmp_ocid} where request.principal.id='${data.oci_database_autonomous_database.starter_atp.autonomous_database_id}'",
        "allow any-user to manage object-family in compartment id ${local.lz_serv_cmp_ocid} where ALL { request.principal.id='${data.oci_database_autonomous_database.starter_atp.autonomous_database_id}', request.permission = 'PAR_MANAGE' }"
    ]
}

