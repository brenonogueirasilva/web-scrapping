terraform {
  backend "gcs" {
    bucket = "terraform-breno-bucket" # GCS bucket name to store terraform tfstate
    prefix = "web_scrapping_trigger"               # Prefix name should be unique for each Terraform project having same remote state bucket.
  }
}
#     backend "local" {}
# }