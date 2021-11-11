data aws_iam_policy_document "trust_policy_allow_nothing" {
  statement {
    sid     = "AllowNothing"
    actions = ["sts:AssumeRole"]
    effect  = "Deny"
    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
  }
}

resource "aws_iam_role" "this" {
  for_each = toset(var.well_known_role_names)
  name = each.value
  assume_role_policy = data.aws_iam_policy_document.trust_policy_allow_nothing.json
}