variable "project_id" {
  type = string
  default = "enduring-branch-413218"
}

variable "region" {
  type = string
  default = "us-central1"
}

variable "service_account_email" {
  type = string
  default = "conta-geral@enduring-branch-413218.iam.gserviceaccount.com"
  
}

variable "service_account_name" {
  type = string
  default = "conta_geral"
  
}

# variable "github_token_file" {
#   description = "Token GitHub"
#   default     = "../github_token.json"
# }

# variable "app_installation_id" {
#   type = number
#   default = 43531708   
# }

# variable "remote_uri" {
#   type = string
#   default = "https://github.com/brenonogueirasilva/api_cloud_build_private.git" 
# }


