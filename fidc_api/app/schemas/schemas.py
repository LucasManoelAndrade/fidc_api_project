from marshmallow import Schema, fields

class FidcCashSchema(Schema):
    fidc_id = fields.Str(required=True)
    available_cash = fields.Float(required=True)
    updated_at = fields.DateTime()

class ProcessingJobSchema(Schema):
    job_id = fields.Str(dump_only=True)
    status = fields.Str()
    created_at = fields.DateTime()
    completed_at = fields.DateTime(allow_none=True)

class OperationSchema(Schema):
    id = fields.Str(required=True)
    asset_code = fields.Str(required=True)
    operation_type = fields.Str(required=True)
    quantity = fields.Int(required=True)
    status = fields.Str()
    execution_price = fields.Float(allow_none=True)
    total_value = fields.Float(allow_none=True)
    tax_paid = fields.Float(allow_none=True)
    created_at = fields.DateTime()

class ExportOperationsSchema(Schema):
    fidc_id = fields.Str(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)