output "iam_service_linked_roles" {
  description = "Map of IAM Service-linked role objects"
  value       = aws_iam_service_linked_role.this
}